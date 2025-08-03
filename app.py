import chainlit as cl
from response_generator import ResponseGenerator
from openai_service import OpenAIService
from brave_search_service import BraveSearchService
from file_processor import FileProcessor
from typing import Dict, Any
import asyncio
import os
import time

# Initialize services
response_gen = ResponseGenerator()
openai_service = OpenAIService()
brave_search = BraveSearchService()
file_processor = FileProcessor()

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    # Initialize user settings
    cl.user_session.set("web_search_enabled", False)
    cl.user_session.set("uploaded_files", [])

    # Add settings controls
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Switch(
                id="web_search_toggle",
                label="Web Search",
                initial=False,
                description="Search current regulations and recent updates"
            )
        ]
    ).send()

async def stream_response(content: str, elements: list = None):
    """Stream response content with proper markdown formatting preserved"""
    msg = cl.Message(content="", elements=elements or [])
    await msg.send()

    # Simply send the complete content at once to preserve formatting
    # The streaming effect is less important than proper formatting
    msg.content = content
    await msg.update()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with enhanced features"""
    user_query = message.content.strip()

    # Handle file attachments if present
    if message.elements:
        await handle_file_attachments(message.elements)

    if not user_query:
        await cl.Message(content="Please provide a question or query.").send()
        return

    # Get user settings and uploaded files
    web_search_enabled = cl.user_session.get("web_search_enabled", False)
    uploaded_files = cl.user_session.get("uploaded_files", [])

    # Show contextual processing steps with clean animations
    if uploaded_files:
        step_name = "Analyzing documents..."
        step_output = "Searching through uploaded documents for relevant information..."
    else:
        step_name = "Processing query..."
        step_output = "Retrieving relevant documents from knowledge base..."

    async with cl.Step(name=step_name) as step:
        step.output = step_output

        try:
            # Generate enhanced response with document context (always use OpenAI refinement)
            result = response_gen.generate_enhanced_response(
                query=user_query,
                use_web_search=web_search_enabled,
                refine_with_openai=True,  # Always enabled
                uploaded_files=uploaded_files  # Pass uploaded files for document-based queries
            )

            # Update step output based on what was found
            output_parts = []

            if result.get('document_context_used'):
                doc_count = len(result.get('document_sources', []))
                output_parts.append(f"✅ Found relevant content in {doc_count} uploaded document(s)")

            if result['documents_found'] > 0:
                output_parts.append(f"📚 {result['documents_found']} knowledge base documents")

            if result.get('web_search_used'):
                web_results_count = len(result.get('web_search_results', {}).get('results', []))
                output_parts.append(f"🌐 {web_results_count} web results")

            if result.get('openai_refinement_used'):
                output_parts.append("🤖 AI enhanced")

            step.output = " | ".join(output_parts) if output_parts else "Processing complete"

        except Exception as e:
            await cl.Message(content=f"❌ An error occurred while processing your query: {str(e)}").send()
            return

    # Prepare the main response
    main_response = result['final_response']

    # Create elements for additional information
    elements = []

    # Add metadata section
    metadata_content = f"## 📊 Response Info\n\n"
    metadata_content += f"- **Confidence**: {result['confidence']:.1%}\n"
    metadata_content += f"- **KB Documents**: {result['documents_found']}\n"
    metadata_content += f"- **Document Context**: {'✅' if result.get('document_context_used') else '❌'}\n"
    metadata_content += f"- **Web Search**: {'✅' if result.get('web_search_used') else '❌'}\n"
    metadata_content += f"- **Uploaded Files**: {len(uploaded_files)}\n"

    elements.append(
        cl.Text(name="metadata", content=metadata_content, display="side")
    )

    # Add sources information
    if result['sources']:
        sources_content = "## Knowledge Base Sources\n\n"
        for i, source in enumerate(result['sources'][:5], 1):
            title = source.get('title', 'Untitled')
            collection = source.get('collection', 'Unknown')
            score = source.get('relevance_score', 0.0)
            sources_content += f"**{i}. {title}**\n"
            sources_content += f"   - Collection: {collection}\n"
            sources_content += f"   - Relevance: {score:.3f}\n\n"

        elements.append(
            cl.Text(name="sources", content=sources_content, display="side")
        )

    # Add web search results if available
    if result.get('web_search_used') and result.get('web_search_results'):
        web_content = brave_search.format_web_results_for_display(result['web_search_results'])
        elements.append(
            cl.Text(name="web_results", content=web_content, display="side")
        )

    # Add document sources if used in response
    if result.get('document_context_used') and result.get('document_sources'):
        doc_sources_content = "## Document Sources Used\n\n"
        for source in result['document_sources']:
            doc_sources_content += f"**{source['name']}**\n"
            doc_sources_content += f"- Relevance: {source['relevance']:.1%}\n"
            doc_sources_content += f"- Type: Uploaded Document\n\n"

        elements.append(
            cl.Text(name="document_sources", content=doc_sources_content, display="side")
        )

    # Add uploaded files information if available
    if uploaded_files:
        files_content = "## All Uploaded Files\n\n"
        for file_info in uploaded_files:
            files_content += f"**{file_info['name']}**\n"
            files_content += f"- Type: {file_info['type']}\n"
            files_content += f"- {file_info['summary']}\n\n"

        elements.append(
            cl.Text(name="uploaded_files", content=files_content, display="side")
        )

    # Send the main response with streaming animation
    await stream_response(main_response, elements)

@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates"""
    cl.user_session.set("web_search_enabled", settings.get("web_search_toggle", False))

    # Notify user of settings change
    web_status = "enabled" if settings.get("web_search_toggle", False) else "disabled"

    await cl.Message(
        content=f"Web Search: {web_status}",
        author="System"
    ).send()

async def handle_file_attachments(elements):
    """Handle file attachments in messages"""
    uploaded_files = cl.user_session.get("uploaded_files", [])

    for element in elements:
        if hasattr(element, 'path') and hasattr(element, 'name'):
            try:
                # Process the uploaded file
                result = file_processor.process_file(element.path, element.name)

                if result['success']:
                    # Store file info in session
                    file_info = {
                        'name': element.name,
                        'type': result['file_type'],
                        'content': result['content'],
                        'summary': result['summary'],
                        'metadata': result['metadata']
                    }
                    uploaded_files.append(file_info)
                    cl.user_session.set("uploaded_files", uploaded_files)

                    # Send confirmation message
                    await cl.Message(
                        content=f"✅ **Document Ready for Analysis!**\n\n"
                               f"📄 **{element.name}**\n"
                               f"📊 {result['summary']}\n\n"
                               f"💡 **Try asking:**\n"
                               f"• \"What does this document contain?\"\n"
                               f"• \"Summarize the key points\"\n"
                               f"• \"What are the main findings?\"\n"
                               f"• Or ask specific questions about the content!",
                        author="System"
                    ).send()

                else:
                    await cl.Message(
                        content=f"❌ **Processing Failed**\n\n"
                               f"File: {element.name}\n"
                               f"Error: {result['error']}\n\n"
                               f"Supported formats: PDF, Word, Excel, CSV",
                        author="System"
                    ).send()

            except Exception as e:
                await cl.Message(
                    content=f"❌ **Error processing {element.name}**: {str(e)}",
                    author="System"
                ).send()

# Removed action buttons to fix validation errors
# Focus on clean, professional interface

if __name__ == "__main__":
    # This will be used when running with chainlit run app.py
    pass
