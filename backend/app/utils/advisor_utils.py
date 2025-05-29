import markdown

def convert_markdown_to_html(markdown_text):
    html_content = markdown.markdown(markdown_text, extensions=["extra", "smarty"])
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{
                background-color: black;
                color: yellow;
                font-family: 'Inter', sans-serif;
                margin: 20px;
            }}
            h1, h2, h3, h4, h5, h6 {{
                font-family: 'Oswald', sans-serif;
                color: orange;
                font-size: 24px;
                margin-bottom: 10px;

            }}
            p, li {{
                font-family: 'Inter', sans-serif;
                color: yellow;
                font-size: 12px;
                line-height: 1.5;
                margin-bottom: 10px;
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Oswald:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    return styled_html