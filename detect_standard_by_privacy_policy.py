import asyncio
import csv
import json
import openai
import os
from dotenv import load_dotenv


class HANDLER:
    @staticmethod
    def remove_empty_lines(content):
        lines = content.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(cleaned_lines)

    @staticmethod
    def ask_gpt(privacy_policy_content):
        try:
            prompt_message = [
                {
                    "role": "system",
                    "content": "You are an expert in classifying privacy policy documents provided by Android applications as Good Standard or Bad Standard, based on the set of definitions below:\n\n I. Good Standard Assessment (Based on GDPR Article 5)\n- Lawfulness, Fairness, and Transparency: Does the policy clearly state its legal basis for data processing? Is the language simple and transparent, making it easy for users to understand how their data is used?\n- Purpose Limitation: Are the purposes for data collection clearly defined and limited? Does the policy ensure data is not used for incompatible purposes without additional consent?\n- Data Minimization: Does the policy specify collecting only necessary data? Is there an emphasis on limiting data collection to what is essential for the stated purpose?\n- Accuracy: Are there measures in place to ensure data accuracy? Does the policy include mechanisms for users to update or correct their data?\n- Storage Limitation: Does the policy define clear retention periods? Are there criteria for determining these periods, and is there a process for data deletion or anonymization after the purpose is fulfilled?\n- Integrity and Confidentiality: Are there adequate security measures to protect data? This includes practices like encryption and regular security assessments.",
                },
                {
                    "role": "user",
                    "content": "Based on the content of the privacy policy below. Please conclude whether the content is Good Standard or Bad Standard ? (NOTE: Please give the result as: | Good or Bad | The reason is brief, giving specific sections ...)\n\n"
                    + privacy_policy_content,
                },
            ]
            response = openai.ChatCompletion.create(
                model=os.getenv("MODEL_GPT4"), messages=prompt_message
            )
            assistant_reply = response.choices[0].message["content"]
            return assistant_reply
        except Exception as e:
            return "Error: The prompt length exceeds the maximum allowed length of 8192 tokens."

    @staticmethod
    async def loop_csv(input_csv_path, output_csv_path):
        with open(input_csv_path, "r", newline="", encoding="utf-8") as csvfile, open(
            output_csv_path, "w", newline="", encoding="utf-8"
        ) as outputfile:

            reader = csv.reader(csvfile)
            writer = csv.writer(outputfile)

            headers = next(reader)
            writer.writerow(headers)

            for index, row in enumerate(reader):
                print(
                    "\n_____________ Run times "
                    + str(index + 1)
                    + " <"
                    + row[1]
                    + "> "
                    + "_____________"
                )
                gpt_result = HANDLER().ask_gpt(row[6])
                row[headers.index("result")] = HANDLER().remove_empty_lines(gpt_result)
                writer.writerow(row)
                print("~~~~~~~~~~~~~~ Success ~~~~~~~~~~~~~~\n")


async def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    input_csv_path = "input_csv_path"
    output_csv_path = "output_csv_path"

    await HANDLER().loop_csv(input_csv_path, output_csv_path)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
