from transformers import pipeline, set_seed

generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")
set_seed(42)

def generate_questions_for_skills(skills: list[str]) -> list[dict]:
    results = []
    for skill in skills:
        prompt = f"Generate two interview questions about {skill}."
        output = generator(prompt, max_length=128, num_return_sequences=1, do_sample=True)[0]['generated_text']
        # Try to split into individual questions (we assume they're returned in a list format)
        if "[" in output:
            try:
                questions = eval(output[output.index("["):])
                if isinstance(questions, list):
                    results.append({"skill": skill, "questions": questions[:2]})
                else:
                    results.append({"skill": skill, "questions": [output]})
            except Exception:
                results.append({"skill": skill, "questions": [output]})
        else:
            results.append({"skill": skill, "questions": [output]})
    return results
