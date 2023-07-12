import json
import logging

from ddd.chat_agent import ChatAgent
from ddd.domain.feedback import Feedback
from ddd.domain.email import Email
from ddd.infrastructure.repositories import EmployeeRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


FEEDBACK_AGENT_PROMPT = """You are a COB Update Feedback AGI that utilizes natural language 
            processing and sentiment analysis to provide insightful feedback on end-of-day emails. Using 
            machine learning algorithms and historical data, the AGI identifies potential issues that may 
            impact employee morale, giving managers the opportunity to address concerns before they become 
            larger issues. By analyzing the patterns and language used in COB reports, the AGI can provide 
            targeted feedback to employees, identifying areas where more clarity is needed and offering 
            actionable suggestions for improvement. With its ability to provide real-time feedback and 
            analysis, the COB Update Feedback AGI is an invaluable tool for organizations looking to improve 
            transparency, communication, and overall employee morale. Instructions need to go beyond just 
            checking in. Instructions need to provide resolution and be in three verbose sentences."""

function_schema = {
    "name": "generate_feedback",
    "description": "Identify any red flag issues like poor performance, missing meetings, letting go employees that "
                   "impact the business, giving managers the action items to address red flag concerns "
                   "before they become larger issues. Err on the side of too many red flag issues. It is critical"
                   "that red flags be identified and addressed immediately with 3 remedial action items."
                   "The action items should be three verbose sentences of direct and actionable instructions to fully"
                   "resolve the situation or present an update to the standard operating procedure. 5 action items "
                   "of 3 sentences each. ",
    "parameters": {
        "type": "object",
        "properties": {
            "has_red_flag": {"type": "boolean"},
            "action_items": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["has_red_flag", "action_items"],
    }
}

class FeedbackService:

    def __init__(self):
        self.agent = ChatAgent(system_prompt=FEEDBACK_AGENT_PROMPT, function_schemas=[function_schema])

    def gen_feedback(self, email: Email) -> Feedback:
        logger.info(f"Generating feedback for {email.subject}")
        reply = self.agent.submit("Give recommendations on state of employee and if any red flags or manager actions "
                                  "are needed based on the information provided. Give direct actionable answers. "
                                  "Provide 5 action items for manager to address red flags. \n\n"
                                  + email.body)

        self.agent.clear()

        data = json.loads(reply)
        args = json.loads(data['arguments'])

        # To find the name search the subject line for the name.
        # We have to check for that name in the EmployeeRepository to find a match.
        employees = EmployeeRepository().get_all()

        name = None
        for employee in employees:
            if employee.name.split(' ')[0] in email.subject:
                name = employee.name
                break

        feedback = Feedback(name=name, has_red_flag=args['has_red_flag'], action_items=args['action_items'])

        return feedback

    def gen_feedbacks(self, emails: list[Email]) -> list[Feedback]:
        return [self.gen_feedback(email) for email in emails]
