import google.generativeai as genai
import ast
import json
import re
from PIL import Image
from constants import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def clean_gemini_response(response_text: str) -> str:
    # Remove markdown code block markers and any 'json' tag
    pattern = r'```(?:json)?\n?(.*?)\n?```'
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_text.strip()

def analyze_image(img: Image, dict_of_vars: dict):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    dict_of_vars_str = json.dumps(dict_of_vars, ensure_ascii=False)
    prompt = (
        f"You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them. "
        f"Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). "
        
        # Original instructions
        f"1. Simple mathematical expressions like `2 + 2`, `3 * 4`, `5 / 6`, etc.: Solve and return in the format: "
        f"[{{'expr': expression, 'result': answer, 'explanation': detailed explanation in Markdown}}]. "
        f"2. Set of Equations like `x^2 + 2x + 1 = 0`, `3y + 4x = 0`, etc.: Solve for each variable, and return each variable with detailed solution steps using Markdown formatting in 'explanation'. "
        f"3. Variable Assignments like `x = 4`, `y = 5`, etc.: Assign values, return each variable with an explanation using Markdown, e.g., 'Assigning value of 4 to x'. "
        f"4. Graphical Problems: Provide a thorough Markdown-formatted explanation for problems shown in graphical form, such as cars colliding, trigonometric problems, etc. "
        f"5. Abstract Concepts: Analyze and explain concepts shown in drawings, using Markdown for clarity. Return in the format: "
        f"[{{'expr': description, 'result': concept, 'explanation': detailed Markdown explanation}}]. "
        
        # Modified instructions for mandatory basic concepts and practice questions
        f"6. Basic Concepts (REQUIRED): For each topic identified in the image, you MUST provide: "
        f"   - A beginner-friendly explanation of the basic concepts involved "
        f"   - Step-by-step breakdown of the fundamental principles "
        f"   - Real-world examples to illustrate the concepts "
        f"   - If it's a drawing, explain the mathematical concepts it represents "
        
        f"7. Practice Questions (REQUIRED): You MUST include 6-7 related questions: "
        f"   - For mathematical problems: include calculation-based questions "
        f"   - For drawings: include conceptual questions about the topic "
        f"   - Questions should be concise and fit in a bubble UI "
        f"   - Make questions engaging and thought-provoking "
        
        f"Format the response to include: "
        f"   'expr': The expression or description "
        f"   'result': The solution or concept "
        f"   'explanation': Detailed explanation in Markdown "
        f"   'basic_concepts': Comprehensive explanation of fundamentals (REQUIRED) "
        f"   'practice_questions': Array of engaging questions (REQUIRED, minimum 3) "
        
        f"Use extra backslashes for escape characters like \\f -> \\\\f, \\n -> \\\\n, etc. "
        f"Here is a dictionary of user-assigned variables. If the given expression has any of these variables, use its actual value: {dict_of_vars_str}. "
        
        f"IMPORTANT: Every response MUST include both 'basic_concepts' and 'practice_questions' fields with meaningful content, regardless of the input type."
    )
    
    response = model.generate_content([prompt, img])
    answers = []
    
    try:
        cleaned_response = clean_gemini_response(response.text)
        
        try:
            answers = json.loads(cleaned_response)
        except json.JSONDecodeError:
            answers = ast.literal_eval(cleaned_response)
            
    except Exception as e:
        print(f"Error in parsing response from Gemini API: {e}")
        # Provide default response if parsing fails
        return [{
            'expr': 'Error processing input',
            'result': 'Unable to analyze',
            'explanation': 'There was an error processing your input. Please try again.',
            'basic_concepts': 'Mathematical problem-solving involves understanding the given information and applying relevant concepts to find a solution.',
            'practice_questions': [
                'Can you identify the key components in this problem?',
                'What mathematical concepts might be relevant here?',
                'How would you approach solving this step by step?'
            ],
            'assign': False
        }]

    print('Parsed answer:', answers)
    
    # Process and validate the answers
    for answer in answers:
        if isinstance(answer, dict):
            answer['assign'] = 'assign' in answer
            
            # Ensure basic_concepts exists and has content
            if 'basic_concepts' not in answer or not answer['basic_concepts']:
                answer['basic_concepts'] = 'This involves understanding mathematical concepts and applying them to solve problems systematically.'
            
            # Ensure practice_questions exists and has at least 3 questions
            if 'practice_questions' not in answer or len(answer['practice_questions']) < 3:
                answer['practice_questions'] = [
                    'How would you approach this problem step by step?',
                    'Can you identify the key concepts involved?',
                    'What similar problems can you think of?'
                ]
            
    return answers
