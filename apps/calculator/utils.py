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
        
        # Modified instructions for mandatory basic concepts, practice questions, and quiz questions
        f"6. Basic Concepts (REQUIRED): For each topic identified in the image, you MUST provide: "
        f"   - A beginner-friendly explanation of the basic concepts involved "
        f"   - Step-by-step breakdown of the fundamental principles "
        f"   - Real-world examples to illustrate the concepts "
        f"   - If it's a drawing, explain the mathematical concepts it represents "
        
        f"7. Practice Questions (REQUIRED): You MUST include 3-4 related questions: "
        f"   - For mathematical problems: include calculation-based questions "
        f"   - For drawings: include conceptual questions about the topic "
        f"   - Questions should be concise and fit in a bubble UI "
        f"   - Make questions engaging and thought-provoking "

        f"8. Quiz Questions (REQUIRED when solution is provided): When you provide a solution, you MUST include: "
        f"   - 15 multiple-choice questions in this format: "
        f"   [{{"
        f"       'question': 'Clear, concise question text',"
        f"       'options': ['option1', 'option2', 'option3', 'option4'],"
        f"       'correctAnswer': 'correct option',"
        f"       'explanation': 'Why this answer is correct'"
        f"   }}] "
        f"   - Questions should test understanding of the concepts "
        f"   - Include a mix of difficulty levels "
        f"   - Ensure explanations are educational "
        f"   -GIVING QUIZ QUESTIONS IS COMPULSORY. EXCEPT IT YOU CANNOT GIVE ANSWER"
        
        f"Format the response to include: "
        f"   'expr': The expression or description "
        f"   'result': The solution or concept "
        f"   'explanation': Detailed explanation in Markdown "
        f"   'basic_concepts': Comprehensive explanation of fundamentals (REQUIRED) "
        f"   'practice_questions': Array of engaging questions (REQUIRED) "
        f"   'quiz_questions': Array of MCQ questions (REQUIRED when solution is provided) "
        
        f"Use extra backslashes for escape characters like \\f -> \\\\f, \\n -> \\\\n, etc. "
        f"Here is a dictionary of user-assigned variables. If the given expression has any of these variables, use its actual value: {dict_of_vars_str}. "
        
        f"IMPORTANT: Every response MUST include 'basic_concepts' and 'practice_questions' fields. Include 'quiz_questions' when a solution is provided."
    )
    
    response = model.generate_content([prompt, img])
    answers = []
    
    try:
        cleaned_response = clean_gemini_response(response.text)
        
        try:
            # Ensure we're getting a list of dictionaries
            answers = json.loads(cleaned_response)
            if not isinstance(answers, list):
                answers = [answers]
            
            # Validate each answer is a dictionary with required fields
            validated_answers = []
            for answer in answers:
                if isinstance(answer, dict):
                    validated_answer = {
                        'expr': answer.get('expr', 'No expression provided'),
                        'result': answer.get('result', 'No result available'),
                        'explanation': answer.get('explanation', 'No explanation available'),
                        'basic_concepts': answer.get('basic_concepts', 'Basic concepts not provided'),
                        'practice_questions': answer.get('practice_questions', [
                            'How would you approach this problem?',
                            'What concepts are involved?',
                            'Can you solve a similar problem?'
                        ]),
                        'quiz_questions': answer.get('quiz_questions', []),
                        'assign': 'assign' in answer
                    }
                    validated_answers.append(validated_answer)
            
            return validated_answers if validated_answers else [{
                'expr': 'Error processing input',
                'result': 'Unable to analyze',
                'explanation': 'Could not parse the AI response properly.',
                'basic_concepts': 'Mathematical problem-solving involves understanding the given information and applying relevant concepts to find a solution.',
                'practice_questions': [
                    'Can you identify the key components in this problem?',
                    'What mathematical concepts might be relevant here?',
                    'How would you approach solving this step by step?'
                ],
                'quiz_questions': []
            }]
            
        except json.JSONDecodeError:
            print("JSON decode error, trying ast.literal_eval")
            raw_answers = ast.literal_eval(cleaned_response)
            if isinstance(raw_answers, list):
                return raw_answers
            return [raw_answers]
            
    except Exception as e:
        print(f"Error in parsing response from Gemini API: {e}")
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
            'quiz_questions': []
        }]

def generate_quiz_questions(topic: str, concepts: str, number_of_questions: int = 15):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    prompt = f"""
    Generate {number_of_questions} multiple-choice quiz questions about {topic}. 
    Use these concepts as reference: {concepts}
    
    Each question should:
    1. Be clear and concise
    2. Have 4 options (A, B, C, D)
    3. Include one correct answer
    4. Include a comprehensive explanation that:
       - Starts from basic principles
       - Explains the concept in detail
       - Provides step-by-step reasoning
       - Can be shown to users who answer incorrectly
    5. Include a real-life application or example of the concept
    
    Format each question as a JSON object with these fields:
    - question: The question text
    - options: Array of 4 possible answers
    - correctAnswer: The correct answer
    - explanation: Detailed explanation from basics (shown if answer is wrong)
    - realLifeUsage: A practical application or example of the concept
    
    Return an array of these question objects.
    
    Example format:
    [
        {{
            "question": "What is the result of 2^3?",
            "options": ["4", "6", "8", "16"],
            "correctAnswer": "8",
            "explanation": "To understand 2^3, let's start with the basics of exponents. An exponent tells us how many times to multiply a number (the base) by itself. In this case, 2^3 means:

            2 × 2 × 2 = 8

            Step-by-step:
            1. Start with 2
            2. Multiply by 2 once: 2 × 2 = 4
            3. Multiply by 2 again: 4 × 2 = 8

            This is different from 2 × 3, which would be 6. With exponents, we're multiplying the base (2) by itself as many times as the exponent (3) indicates.",
            "realLifeUsage": "Exponents are widely used in real life. For example:
            1. In computer science, file sizes often use powers of 2 (2^10 bytes = 1 kilobyte, 2^20 bytes = 1 megabyte).
            2. In biology, bacterial growth can often be modeled using exponential functions.
            3. In finance, compound interest calculations use exponents to determine how investments grow over time."
        }},
        ...
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_response = clean_gemini_response(response.text)
        questions = json.loads(cleaned_response)
        
        # Validate and format questions
        formatted_questions = []
        for q in questions:
            if all(key in q for key in ['question', 'options', 'correctAnswer', 'explanation', 'realLifeUsage']):
                formatted_questions.append({
                    'question': q['question'],
                    'options': q['options'],
                    'correctAnswer': q['correctAnswer'],
                    'explanation': q['explanation'],
                    'realLifeUsage': q['realLifeUsage']
                })
        
        return formatted_questions[:number_of_questions]  # Ensure we return exactly the requested number
        
    except Exception as e:
        print(f"Error generating quiz questions: {str(e)}")
        # Return some default questions if generation fails
        return [{
            'question': 'There was an error generating custom questions. Here is a sample question.',
            'options': [
                'Option A',
                'Option B',
                'Option C',
                'Option D'
            ],
            'correctAnswer': 'Option A',
            'explanation': 'This is a sample question due to an error in generation. In a real scenario, this explanation would provide a comprehensive breakdown of the concept, starting from basic principles and explaining step-by-step how to arrive at the correct answer.',
            'realLifeUsage': 'In a real scenario, this would describe a practical application or example of how this concept is used in everyday life or in specific fields.'
        }]
