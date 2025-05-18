# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import json
import os
import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ReminderScheduled

# Load the schemes data
def load_schemes_data():
    try:
        with open('data/schemes.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading schemes data: {e}")
        return []

class ActionListSchemes(Action):
    def name(self) -> Text:
        return "action_list_schemes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Check if we're filtering by scheme type
        scheme_type = tracker.get_slot("scheme_type")
        state = tracker.get_slot("state")
        
        filtered_schemes = schemes
        
        # Filter by type if specified
        if scheme_type:
            filtered_schemes = [s for s in schemes if s.get("type ", "").lower() == scheme_type.lower()]
        
        # Filter by state if specified
        if state:
            filtered_schemes = [s for s in filtered_schemes if s.get("applicable_state", "").lower() == state.lower()]
        
        if not filtered_schemes:
            dispatcher.utter_message(text=f"I couldn't find any schemes matching your criteria.")
            return []
        
        # Prepare response message
        if scheme_type:
            message = f"Here are the {scheme_type} schemes I found:\n\n"
        else:
            message = "Here are the available government schemes:\n\n"
        
        # List the schemes with numbers
        for i, scheme in enumerate(filtered_schemes, 1):
            message += f"{i}. {scheme.get('name', 'Unknown Scheme')}\n"
        
        message += "\nYou can ask me for more details about any specific scheme."
        dispatcher.utter_message(text=message)
        
        return []

class ActionSchemeDetails(Action):
    def name(self) -> Text:
        return "action_scheme_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the scheme name from slot
        scheme_name = tracker.get_slot("scheme")
        
        if not scheme_name:
            dispatcher.utter_message(text="Which scheme would you like to know more about?")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Find the scheme
        scheme = next((s for s in schemes if s.get("name", "").lower() == scheme_name.lower()), None)
        
        if not scheme:
            dispatcher.utter_message(text=f"I couldn't find information about {scheme_name}. Please check the name and try again.")
            return []
        
        # Format scheme details
        message = f"📝 **{scheme.get('name', 'Unknown Scheme')}**\n\n"
        message += f"Type: {scheme.get('type ', 'Not specified')}\n"
        message += f"State: {scheme.get('applicable_state', 'Not specified')}\n"
        message += f"Eligible for: {scheme.get('eligible_for', 'Not specified')}\n"
        message += f"Income limit: ₹{scheme.get('income_limit', 'Not specified')}\n"
        message += f"Required documents: {scheme.get('documents_required', 'Not specified')}\n"
        
        # Add application dates
        start_date = scheme.get('start_date', 'Not specified')
        end_date = scheme.get('end_date', 'Not specified')
        message += f"Application period: {start_date} to {end_date}\n"
        
        # Add application link
        application_link = scheme.get('application_link', '')
        if application_link:
            message += f"\nYou can apply at: {application_link}"
        
        dispatcher.utter_message(text=message)
        
        return []

class ActionCheckEligibility(Action):
    def name(self) -> Text:
        return "action_check_eligibility"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the scheme name from slot
        scheme_name = tracker.get_slot("scheme")
        
        if not scheme_name:
            dispatcher.utter_message(text="Which scheme's eligibility criteria would you like to know about?")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Find the scheme
        scheme = next((s for s in schemes if s.get("name", "").lower() == scheme_name.lower()), None)
        
        if not scheme:
            dispatcher.utter_message(text=f"I couldn't find eligibility information for {scheme_name}.")
            return []
        
        # Format eligibility details
        message = f"Eligibility criteria for **{scheme.get('name', 'Unknown Scheme')}**:\n\n"
        message += f"• Eligible groups: {scheme.get('eligible_for', 'Not specified')}\n"
        message += f"• Income limit: ₹{scheme.get('income_limit', 'Not specified')}\n"
        message += f"• Applicable state: {scheme.get('applicable_state', 'Not specified')}\n"
        
        dispatcher.utter_message(text=message)
        
        return []

class ActionRequiredDocuments(Action):
    def name(self) -> Text:
        return "action_required_documents"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the scheme name from slot
        scheme_name = tracker.get_slot("scheme")
        
        if not scheme_name:
            dispatcher.utter_message(text="Which scheme's document requirements would you like to know about?")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Find the scheme
        scheme = next((s for s in schemes if s.get("name", "").lower() == scheme_name.lower()), None)
        
        if not scheme:
            dispatcher.utter_message(text=f"I couldn't find document information for {scheme_name}.")
            return []
        
        # Check if document info is available
        documents = scheme.get("documents_required", "")
        
        if not documents:
            dispatcher.utter_message(text=f"I don't have information about required documents for {scheme_name}.")
            return []
        
        # Format document details
        message = f"Documents required for **{scheme.get('name', 'Unknown Scheme')}**:\n\n"
        
        # Split the documents by comma and list them
        doc_list = [doc.strip() for doc in documents.split(",")]
        for doc in doc_list:
            message += f"• {doc}\n"
        
        dispatcher.utter_message(text=message)
        
        return []

class ActionApplicationProcess(Action):
    def name(self) -> Text:
        return "action_application_process"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the scheme name from slot
        scheme_name = tracker.get_slot("scheme")
        
        if not scheme_name:
            dispatcher.utter_message(text="Which scheme's application process would you like to know about?")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Find the scheme
        scheme = next((s for s in schemes if s.get("name", "").lower() == scheme_name.lower()), None)
        
        if not scheme:
            dispatcher.utter_message(text=f"I couldn't find application information for {scheme_name}.")
            return []
        
        # Format application process details
        message = f"Application process for **{scheme.get('name', 'Unknown Scheme')}**:\n\n"
        message += "1. Check your eligibility based on income and category criteria\n"
        message += "2. Gather all required documents:\n"
        
        # List required documents
        documents = scheme.get("documents_required", "Not specified")
        doc_list = [doc.strip() for doc in documents.split(",")]
        for doc in doc_list:
            message += f"   • {doc}\n"
        
        message += f"3. Visit the official application portal: {scheme.get('application_link', 'Not specified')}\n"
        message += "4. Create an account or login if you already have one\n"
        message += "5. Fill the application form with accurate information\n"
        message += "6. Upload scanned copies of all required documents\n"
        message += "7. Submit the application and note your application ID\n"
        message += "8. Track your application status regularly\n"
        
        # Add deadline information
        end_date = scheme.get("end_date", "Not specified")
        message += f"\nMake sure to complete your application before: {end_date}"
        
        dispatcher.utter_message(text=message)
        
        return []

class ActionCheckDeadline(Action):
    def name(self) -> Text:
        return "action_check_deadline"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the scheme name from slot
        scheme_name = tracker.get_slot("scheme")
        
        if not scheme_name:
            dispatcher.utter_message(text="Which scheme's deadline would you like to know about?")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Find the scheme
        scheme = next((s for s in schemes if s.get("name", "").lower() == scheme_name.lower()), None)
        
        if not scheme:
            dispatcher.utter_message(text=f"I couldn't find deadline information for {scheme_name}.")
            return []
        
        # Get deadline info
        start_date = scheme.get("start_date", "Not specified")
        end_date = scheme.get("end_date", "Not specified")
        
        # Calculate days remaining if end_date is available
        days_remaining = "unknown"
        if end_date != "Not specified":
            try:
                end_datetime = datetime.datetime.strptime(end_date, "%d-%m-%Y")
                today = datetime.datetime.now()
                delta = end_datetime - today
                days_remaining = delta.days
            except Exception as e:
                print(f"Error calculating days remaining: {e}")
        
        # Format deadline message
        message = f"Application timeline for **{scheme.get('name', 'Unknown Scheme')}**:\n\n"
        message += f"• Start date: {start_date}\n"
        message += f"• Last date: {end_date}\n"
        
        if isinstance(days_remaining, int):
            if days_remaining < 0:
                message += "\n⚠️ The application deadline has passed."
            elif days_remaining == 0:
                message += "\n⚠️ Today is the last day to apply!"
            elif days_remaining <= 7:
                message += f"\n⚠️ Only {days_remaining} days left to apply! Don't miss it."
            else:
                message += f"\n✅ You have {days_remaining} days left to apply."
        
        dispatcher.utter_message(text=message)
        
        return []

class ActionIncomeLimit(Action):
    def name(self) -> Text:
        return "action_income_limit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the scheme name from slot
        scheme_name = tracker.get_slot("scheme")
        
        if not scheme_name:
            dispatcher.utter_message(text="Which scheme's income limit would you like to know about?")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Find the scheme
        scheme = next((s for s in schemes if s.get("name", "").lower() == scheme_name.lower()), None)
        
        if not scheme:
            dispatcher.utter_message(text=f"I couldn't find income limit information for {scheme_name}.")
            return []
        
        # Get income limit
        income_limit = scheme.get("income_limit", "Not specified")
        
        # Format response
        message = f"Income limit for **{scheme.get('name', 'Unknown Scheme')}**:\n\n"
        message += f"The annual family income should be less than ₹{income_limit} to be eligible for this scheme."
        
        dispatcher.utter_message(text=message)
        
        return []

class ActionSetReminder(Action):
    def name(self) -> Text:
        return "action_set_reminder"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the scheme name from slot
        scheme_name = tracker.get_slot("scheme")
        
        if not scheme_name:
            dispatcher.utter_message(text="Which scheme would you like to set a reminder for?")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Find the scheme
        scheme = next((s for s in schemes if s.get("name", "").lower() == scheme_name.lower()), None)
        
        if not scheme:
            dispatcher.utter_message(text=f"I couldn't find deadline information for {scheme_name} to set a reminder.")
            return []
        
        # Get deadline info
        end_date = scheme.get("end_date", "")
        
        if not end_date:
            dispatcher.utter_message(text=f"I don't have deadline information for {scheme_name}, so I can't set a reminder.")
            return []
        
        # Set reminder 3 days before deadline
        try:
            end_datetime = datetime.datetime.strptime(end_date, "%d-%m-%Y")
            reminder_datetime = end_datetime - datetime.timedelta(days=3)
            
            if reminder_datetime < datetime.datetime.now():
                dispatcher.utter_message(text=f"The deadline for {scheme_name} is too close or has passed, so I can't set a reminder.")
                return []
            
            reminder_text = f"⏰ Reminder: The application deadline for {scheme_name} is in 3 days ({end_date}). Don't miss it!"
            
            # Create reminder event
            reminder = ReminderScheduled(
                "EXTERNAL_reminder",
                trigger_date_time=reminder_datetime,
                name=f"reminder_{scheme_name.replace(' ', '_')}",
                kill_on_user_message=False,
            )
            
            dispatcher.utter_message(text=f"I've set a reminder for {scheme_name}. You'll be notified 3 days before the deadline ({end_date}).")
            
            return [reminder]
            
        except Exception as e:
            print(f"Error setting reminder: {e}")
            dispatcher.utter_message(text=f"I couldn't set a reminder for {scheme_name} due to a technical issue.")
            return []

class ActionApplicationLink(Action):
    def name(self) -> Text:
        return "action_application_link"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the scheme name from slot
        scheme_name = tracker.get_slot("scheme")
        
        if not scheme_name:
            dispatcher.utter_message(text="Which scheme's application link would you like to know?")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Find the scheme
        scheme = next((s for s in schemes if s.get("name", "").lower() == scheme_name.lower()), None)
        
        if not scheme:
            dispatcher.utter_message(text=f"I couldn't find application link for {scheme_name}.")
            return []
        
        # Get application link
        application_link = scheme.get("application_link", "")
        
        if not application_link:
            dispatcher.utter_message(text=f"I don't have the application link for {scheme_name}.")
            return []
        
        # Format response
        message = f"Application link for **{scheme.get('name', 'Unknown Scheme')}**:\n\n"
        message += f"{application_link}\n\n"
        message += "Make sure to have all required documents ready before starting the application process."
        
        dispatcher.utter_message(text=message)
        
        return []

class ActionRecommendSchemes(Action):
    def name(self) -> Text:
        return "action_recommend_schemes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get user profile information
        eligibility_category = tracker.get_slot("eligibility_category")
        income = tracker.get_slot("income")
        state = tracker.get_slot("state") or "Uttar Pradesh"  # Default to UP if not specified
        
        if not eligibility_category:
            dispatcher.utter_message(text="I need more information about you to recommend schemes. Please tell me which category you belong to (SC/ST/OBC/General/Female/Minority/BPL etc.)")
            return []
        
        # Get schemes data
        schemes = load_schemes_data()
        
        # Filter schemes based on user profile
        recommended_schemes = []
        
        for scheme in schemes:
            eligible_for = scheme.get("eligible_for", "").lower()
            
            # Check if eligibility matches
            if eligibility_category.lower() in eligible_for:
                recommended_schemes.append(scheme)
            # Special cases for better matching
            elif eligibility_category.lower() == "sc" and "sc students" in eligible_for:
                recommended_schemes.append(scheme)
            elif eligibility_category.lower() == "st" and "st students" in eligible_for:
                recommended_schemes.append(scheme)
            elif eligibility_category.lower() == "obc" and "obc students" in eligible_for:
                recommended_schemes.append(scheme)
            elif eligibility_category.lower() == "general" and "general students" in eligible_for:
                recommended_schemes.append(scheme)
            elif eligibility_category.lower() == "female" and ("female" in eligible_for or "girl" in eligible_for or "women" in eligible_for):
                recommended_schemes.append(scheme)
            elif eligibility_category.lower() == "minority" and "minority" in eligible_for:
                recommended_schemes.append(scheme)
            elif eligibility_category.lower() == "bpl" and ("bpl" in eligible_for or "below poverty" in eligible_for):
                recommended_schemes.append(scheme)
        
        if not recommended_schemes:
            dispatcher.utter_message(text=f"I couldn't find any schemes specifically for {eligibility_category} category. You may still be eligible for general schemes.")
            return []
        
        # Format recommendations
        message = f"Based on your {eligibility_category} category, I recommend these schemes:\n\n"
        
        for i, scheme in enumerate(recommended_schemes, 1):
            message += f"{i}. {scheme.get('name', 'Unknown Scheme')}\n"
            end_date = scheme.get("end_date", "Not specified")
            message += f"   Deadline: {end_date}\n"
        
        message += "\nYou can ask me for more details about any of these schemes."
        dispatcher.utter_message(text=message)
        
        return []
