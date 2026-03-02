import re

def generate_structogram_html(pseudocode: str) -> str:
    def escape_html(text: str) -> str:
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace('§n', '<br>')
        text = text.replace('§_','<u>').replace('_§', '</u>')
        text = text.replace('§*', '<b>').replace('*§', '</b>')
        text = text.replace('§#', '<i>').replace('#§', '</i>')
        text = text.replace('§(', '<i style="color:#a5adcb; text-align: right;">&emsp;').replace(')§', '</i>')
        text = text.replace('§t', '&emsp;')
        text = text.replace('§s', '&nbsp')
        return text

    def format_statement(text: str) -> str:
        text = escape_html(text)
        text = re.sub(r'\b(return)\b', r'<b>\1</b>', text)
        return f"<struct-sequence>{text}</struct-sequence>\n"

    def tokenize(code: str):
        tokens = []
        in_multiline_comment = False
        in_multiline_statement = False
        multiline_buf = []

        for line in code.split('\n'):
            original_line = line
            line = line.strip()
            if not line:
                continue

            # 1. Handle Multiline Comments (Displayed)
            if in_multiline_comment:
                if '*/' in line:
                    idx = line.find('*/')
                    multiline_buf.append(line[:idx].strip())
                    tokens.append(['MULTI_COMMENT', '\n'.join(multiline_buf).strip()])
                    in_multiline_comment = False
                else:
                    multiline_buf.append(line)
                continue
            
            if in_multiline_statement:
                if line == ']':
                    in_multiline_statement = False
                else:
                    if tokens[-1][1] == '':
                        tokens[-1][1] = line
                    else:
                        tokens[-1][1] += ' §n ' + line
                continue


                    

            if line.startswith('/*'):
                if '*/' in line:
                    start = line.find('/*') + 2
                    end = line.find('*/')
                    tokens.append(['MULTI_COMMENT', line[start:end].strip()])
                else:
                    in_multiline_comment = True
                    multiline_buf = [line[2:].strip()]
                continue
            
            if line == '[':
                in_multiline_statement = True
                tokens.append(['STATEMENT', ''])
                continue

            # 2. Handle '#' Comments (Not displayed)
            if '#' in line:
                line = line.split('#')[0].strip()
                if not line:
                    continue
            
            # 


            # 3. Handle '//' Comments (Displayed)
            if line.startswith('//'):
                tokens.append(['COMMENT', line[2:].strip()])
                continue

            # 4. Keyword extraction
            lower_line = line.lower()
            if lower_line.startswith('caption '):
                tokens.append(['CAPTION', line[8:].strip()])
            elif lower_line.startswith('if '):
                tokens.append(['IF', line[3:].strip()])
            elif lower_line == 'else':
                tokens.append(['ELSE', ''])
            elif lower_line == 'end':
                tokens.append(['END', ''])
            elif lower_line.startswith('while '):
                tokens.append(['WHILE', line[6:].strip()])
            elif lower_line.startswith('for '):
                tokens.append(['WHILE', line[4:].strip()])
            elif lower_line == 'do':
                tokens.append(['DO', ''])
            elif lower_line.startswith('switch'):
                tokens.append(['SWITCH', line[6:].strip()])
            elif lower_line.startswith('case '):
                tokens.append(['CASE', line[5:].strip()])
            else:
                
                #txt = original_line.strip()
                #if (1 < len(tokens) and tokens[-1][0] == 'CASE'):

                
                tokens.append(['STATEMENT', original_line.strip()])
                




        return tokens

    # Disambiguate 'WHILE_START' (pre-test) vs 'DO_WHILE' (post-test) 
    def tag_while_loops(tokens):
        stack = []
        for i in range(len(tokens) - 1, -1, -1):
            tok_type, val = tokens[i]
            if tok_type == 'END':
                stack.append('END')
            elif tok_type == 'WHILE':
                if stack and stack[-1] == 'END':
                    stack.pop() # Pre-test loop matched with END
                else:
                    tokens[i][0] = 'DO_WHILE' # Post-test loop closes a DO
                    stack.append('DO_WHILE')
            elif tok_type in ('IF', 'SWITCH'):
                if stack and stack[-1] == 'END': stack.pop()
            elif tok_type == 'DO':
                if stack and stack[-1] == 'DO_WHILE': stack.pop()
        return tokens

    # Setup the token stream
    raw_tokens = tokenize(pseudocode)
    tokens = tag_while_loops(raw_tokens)
    
    caption = "Algorithm"
    filtered_tokens = []
    for t_type, val in tokens:
        if t_type == 'CAPTION':
            caption = escape_html(val)
        else:
            filtered_tokens.append([t_type, val])

    iterator = iter(filtered_tokens)

    # Recursive Parser
    def parse_block(end_types):
        html = ""
        while True:
            try:
                token_type, value = next(iterator)
            except StopIteration:
                return html, "EOF", ""

            if token_type in end_types:
                return html, token_type, value

            if token_type == 'STATEMENT':
                html += format_statement(value)
            elif token_type in ('COMMENT', 'MULTI_COMMENT'):
                # Preserve line breaks for multi-line comments
                html += f"<struct-comment>{escape_html(value)}</struct-comment>\n"
            
            elif token_type == 'IF':
                then_html, end_tok, end_val = parse_block(['ELSE', 'END'])
                if_html = f'<struct-decision condition="{escape_html(value)}">\n<struct-block>\n{then_html}</struct-block>\n'
                closing_tags = '</struct-decision>\n'
                    
                if end_tok == 'ELSE':
                    else_html, end_tok, end_val = parse_block(['END'])
                    if_html += f'<struct-block>\n{else_html}</struct-block>\n'
                else: 
                    # End IF prematurely, leaving an empty ELSE block (required by structoview.js)
                    if_html += f'<struct-block></struct-block>\n'
                    
                html += if_html + closing_tags

            elif token_type == 'WHILE':
                body, _, _ = parse_block(['END'])
                html += f'<struct-iteration condition="{escape_html(value)}">\n<struct-block>\n{body}</struct-block>\n</struct-iteration>\n'

            elif token_type == 'DO':
                body, _, end_val = parse_block(['DO_WHILE'])
                html += f'<struct-loop condition="{escape_html(end_val)}">\n<struct-block>\n{body}</struct-block>\n</struct-loop>\n'

            elif token_type == 'SWITCH':
                switch_html = f'<struct-select condition="{escape_html(value)}">\n'
                first_case = True
                while True:
                    part_html, tok, val = parse_block(['CASE', 'END'])
                    if not first_case:
                        switch_html += f'{part_html}</struct-block>\n</struct-case>\n'
                    if tok == 'CASE':
                        cond = escape_html(val)
                        # Add a hidden element to force the block to be at least as wide as the condition
                        phantom = f'<div style="height:0;overflow:hidden;visibility:hidden;font-size:0.75em;white-space:nowrap;padding:0 0.5em;">{cond}</div>'
                        switch_html += f'<struct-case condition="{cond}">\n<struct-block>\n{phantom}'
                        first_case = False
                    elif tok == 'END':
                        break
                # Default empty block required by structoview.css architecture
                # switch_html += '<struct-block></struct-block>\n</struct-select>\n'
                switch_html += '</struct-select>\n'
                html += switch_html

    body_html, _, _ = parse_block([])
    return f'<struct-diagram caption="{caption}">\n\n{body_html}</struct-diagram>'