import markdown


def preprocess_markdown(markdown_text):
    # Example: Normalize spacing and fix common issues
    markdown_text = markdown_text.strip()
    markdown_text = markdown_text.replace("**;", "**")  # Fix malformed bold syntax
    markdown_text = markdown_text.replace("\n\n", "\n")  # Remove excessive newlines
    return markdown_text


def convert_markdown_to_html(markdown_text):
    markdown_text = preprocess_markdown(markdown_text)  # Preprocess markdown

    html_content = markdown.markdown(markdown_text, extensions=["extra", "smarty"])
    styled_html = f"""
    <html>
        <style>
            ul, ol {{
                margin-left: 30px; /* Indent list items */
            }}
            li {{
                margin-bottom: 10px; /* Add spacing between items */
            }}
            p {{
                margin-left: 10px;
            }}
        </style>
    <body>
        {html_content}
    </body>
    </html>
    """
    return styled_html
