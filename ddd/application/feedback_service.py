from chat_agent import ChatAgent
from ddd.domain import Feedback, Email

FEEDBACK_AGENT_PROMPT = """You are a COB Update Feedback AGI that utilizes natural language 
            processing and sentiment analysis to provide insightful feedback on end-of-day emails. Using 
            machine learning algorithms and historical data, the AGI identifies potential issues that may 
            impact employee morale, giving managers the opportunity to address concerns before they become 
            larger issues. By analyzing the patterns and language used in COB reports, the AGI can provide 
            targeted feedback to employees, identifying areas where more clarity is needed and offering 
            actionable suggestions for improvement. With its ability to provide real-time feedback and 
            analysis, the COB Update Feedback AGI is an invaluable tool for organizations looking to improve 
            transparency, communication, and overall employee morale."""


class FeedbackService:

    def __init__(self):
        self.agent = ChatAgent(system_prompt=FEEDBACK_AGENT_PROMPT)

    def gen_feedback(self, text: str) -> Feedback:
        reply = self.agent.submit("Give recommendations on state of employee and if any mgr actions are needed "
                                  "based on the information provided. Give direct actionable answers. Add <<RED_FLAG>> "
                                  "if there is an issue that could possibly need manager intervention. "
                                  "Response should be elegantly formatted with 3 bullet points. The first line is the"
                                  "first name and last name of the sender:\n\n"
                                  "{{sender_first_and_last_name}}\n{{summary}}"
                                  "\n\n- {{bullet_point}}\n- {{bullet_point}}\n"
                                  "- {{bullet_point}}\n{{has_red_flag}}" + text)

        self.agent.clear()

        name = reply.splitlines()[0].strip()

        feedback = Feedback(name=name, content=reply)

        return feedback

    def gen_feedbacks(self, emails: list[Email]) -> list[Feedback]:
        return [self.gen_feedback(email.body) for email in emails]
