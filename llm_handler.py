from groq import Groq
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from data_analyzer import DataAnalyzer
import json
from datetime import datetime
import pandas as pd

load_dotenv()

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        return super().default(obj)

class LLMHandler:
    def __init__(self, file_path: str):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.analyzer = DataAnalyzer(file_path)
        self.file_path = file_path
        self.conversation_history = []
    
    def get_answer(self, question: str) -> str:
        """Main method to get answers with conversation history"""
        # Add user question to history
        self._add_to_history(question, "user")
        
        # First try to answer with direct analysis
        analysis_result = self.analyzer.query(question)
        
        # Format the analysis result
        direct_answer = self._format_analysis_result(analysis_result, question)
        if direct_answer and not direct_answer.startswith("Could not"):
            self._add_to_history(direct_answer, "assistant")
            return direct_answer
        
        # Fallback to LLM for complex questions
        llm_answer = self._ask_llm(question, analysis_result)
        self._add_to_history(llm_answer, "assistant")
        return llm_answer
    
    def _format_analysis_result(self, result: Dict, question: str) -> Optional[str]:
        """Convert analysis results to natural language"""
        if result['type'] == 'department_count':
            return f"Answer: {result['count']} employees in {result['department']} department: {', '.join(result['names'])}"
        
        elif result['type'] == 'employee_salary':
            return f"Answer: {result['name']}'s salary is ${result['salary']:,.2f}"
        
        elif result['type'] == 'highest_salary':
            return f"Answer: {result['name']} has the highest salary (${result['salary']:,.2f}) in {result['department']} department"
        
        elif result['type'] == 'sales_count':
            return f"Answer: {result['count']} sales in {result['month']} (SaleIDs: {', '.join(map(str, result['sale_ids']))})"
        
        elif result['type'] == 'recent_hire':
            return f"Answer: {result['name']} was hired most recently on {result['hire_date'].strftime('%Y-%m-%d')} in {result['department']} department"
        
        elif result['type'] == 'feedback_score':
            return f"Answer: {result['name']}'s FeedbackScore is {result['score']} ({result['comment']})"
        
        elif result['type'] == 'employee_department':
            return f"Answer: {result['name']} belongs to {result['department']} department"
        
        elif result['type'] == 'sale_amount':
            return f"Answer: SalesAmount for SaleID {result['sale_id']} is ${result['amount']:,.2f}"
        
        elif result['type'] == 'needs_improvement':
            return f"Answer: {result['name']} received 'Needs Improvement' feedback (FeedbackID: {result['feedback_id']})"
        
        elif result['type'] == 'total_sales':
            return f"Answer: Total sales for {result['month']} is ${result['total']:,.2f}"
        
        elif result['type'] == 'top_sales_employee':
            return f"Answer: {result['name']} has the highest total sales (${result['total_sales']:,.2f})"
        
        elif result['type'] == 'avg_salary':
            return f"Answer: Average salary in {result['department']} department is ${result['average']:,.2f}"
        
        elif result['type'] == 'feedback_count':
            return f"Answer: {result['count']} employees have FeedbackScore of {result['score']}"
        
        elif result['type'] == 'total_payroll':
            return f"Answer: Total payroll expense is ${result['total']:,.2f}"
        
        elif result['type'] == 'top_sales_month':
            return f"Answer: {result['month']} had the highest total sales (${result['total']:,.2f})"
        
        elif result['type'] == 'avg_feedback':
            return f"Answer: Average FeedbackScore across all employees is {result['average']:.2f}"
        
        elif result['type'] == 'lowest_avg_salary':
            return f"Answer: {result['department']} department has the lowest average salary (${result['average']:,.2f})"
        
        elif result['type'] == 'employees_before_year':
            return f"Answer: {result['count']} employees were hired before {result['year']}: {', '.join(result['names'])}"
        
        elif result['type'] == 'most_feedback':
            return f"Answer: {result['name']} has the most feedback entries ({result['count']})"
        
        elif 'error' in result:
            return f"Answer: {result['error']}"
        
        return None
    
    def _ask_llm(self, question: str, analysis_result: Dict = None) -> str:
        """Use LLM for complex questions with conversation history"""
        # Prepare context
        context = {
            "file": self.file_path,
            "sheets": {
                name: {
                    "columns": sheet.data.columns.tolist(),
                    "sample_data": json.loads(json.dumps(sheet.data.head(2).to_dict('records'), cls=EnhancedJSONEncoder))
                }
                for name, sheet in self.analyzer.sheets.items()
            },
            "conversation_history": self.conversation_history[-5:]  # Last 5 messages
        }
        
        if analysis_result and 'error' not in analysis_result:
            context['analysis'] = json.loads(json.dumps(analysis_result, cls=EnhancedJSONEncoder))
        
        try:
            prompt = f"""You are a data analyst assistant. Given this context:
            {json.dumps(context, indent=2, cls=EnhancedJSONEncoder)}
            
            Current question: {question}
            
            Please provide a concise answer based on the data and conversation history.
            Format: "Answer: [your response]"
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Answer: Error processing your question: {str(e)}"
    
    def _add_to_history(self, text: str, role: str):
        """Maintain conversation history"""
        self.conversation_history.append({"role": role, "content": text})
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []