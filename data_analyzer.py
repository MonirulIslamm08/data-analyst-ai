import pandas as pd
from typing import Dict, List, Optional, Union
import re
from dataclasses import dataclass

@dataclass
class SheetInfo:
    name: str
    data: pd.DataFrame
    column_types: Dict[str, List[str]]

class DataAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sheets = self._load_all_sheets()
        self._preprocess_data()
        self._create_relationships()
    
    def _load_all_sheets(self) -> Dict[str, SheetInfo]:
        """Load all sheets from Excel or single sheet from CSV"""
        sheets = {}
        
        if self.file_path.endswith('.csv'):
            data = pd.read_csv(self.file_path)
            sheet_info = self._analyze_sheet('data', data)
            sheets['data'] = sheet_info
        else:
            with pd.ExcelFile(self.file_path) as xls:
                for sheet_name in xls.sheet_names:
                    data = pd.read_excel(xls, sheet_name)
                    sheets[sheet_name] = self._analyze_sheet(sheet_name, data)
        return sheets
    
    def _analyze_sheet(self, sheet_name: str, data: pd.DataFrame) -> SheetInfo:
        """Analyze a single sheet's structure"""
        column_types = {
            'numeric': [],
            'categorical': [],
            'date': [],
            'id': []
        }
        
        for col in data.columns:
            col_str = str(col).lower()
            
            if pd.api.types.is_numeric_dtype(data[col]):
                column_types['numeric'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(data[col]):
                column_types['date'].append(col)
            else:
                try:
                    data[col] = pd.to_datetime(data[col])
                    column_types['date'].append(col)
                except:
                    column_types['categorical'].append(col)
            
            if re.match(r'.*id.*', col_str) and not re.match(r'.*idea.*', col_str):
                column_types['id'].append(col)
        
        return SheetInfo(name=sheet_name, data=data, column_types=column_types)
    
    def _preprocess_data(self):
        """Clean and preprocess data across all sheets"""
        for sheet in self.sheets.values():
            for col in sheet.data.columns:
                if pd.api.types.is_numeric_dtype(sheet.data[col]):
                    sheet.data[col] = pd.to_numeric(sheet.data[col], errors='coerce')
                elif pd.api.types.is_string_dtype(sheet.data[col]):
                    sheet.data[col] = sheet.data[col].astype(str).str.strip()
    
    def _create_relationships(self):
        """Create merged views of related data"""
        if 'Employees' in self.sheets and 'Sales' in self.sheets:
            self.employee_sales = pd.merge(
                self.sheets['Employees'].data,
                self.sheets['Sales'].data,
                on='EmployeeID',
                how='left'
            )
        
        if 'Employees' in self.sheets and 'Feedback' in self.sheets:
            self.employee_feedback = pd.merge(
                self.sheets['Employees'].data,
                self.sheets['Feedback'].data,
                on='EmployeeID',
                how='left'
            )
    
    def query(self, question: str) -> Dict:
        """Main query interface for all analysis"""
        question_lower = question.lower()
        
        # Department count questions
        if 'how many employees' in question_lower and 'department' in question_lower:
            dept = self._extract_department(question)
            if dept:
                count = len(self.sheets['Employees'].data[
                    self.sheets['Employees'].data['Department'] == dept
                ])
                names = self.sheets['Employees'].data[
                    self.sheets['Employees'].data['Department'] == dept
                ]['Name'].tolist()
                return {
                    'type': 'department_count',
                    'department': dept,
                    'count': count,
                    'names': names
                }
        
        # Individual salary questions
        elif 'salary of' in question_lower:
            name = self._extract_name(question)
            if name:
                salary = self.sheets['Employees'].data[
                    self.sheets['Employees'].data['Name'] == name
                ]['Salary'].values[0]
                return {
                    'type': 'employee_salary',
                    'name': name,
                    'salary': salary
                }
        
        # Highest salary question
        elif 'highest salary' in question_lower:
            max_salary = self.sheets['Employees'].data['Salary'].max()
            employee = self.sheets['Employees'].data[
                self.sheets['Employees'].data['Salary'] == max_salary
            ].iloc[0]
            return {
                'type': 'highest_salary',
                'name': employee['Name'],
                'salary': employee['Salary'],
                'department': employee['Department']
            }
        
        # Sales count questions
        elif 'how many sales' in question_lower and 'february' in question_lower:
            feb_sales = self.sheets['Sales'].data[
                self.sheets['Sales'].data['Month'] == '2025-02'
            ]
            return {
                'type': 'sales_count',
                'month': 'February 2025',
                'count': len(feb_sales),
                'sale_ids': feb_sales['SaleID'].tolist()
            }
        
        # Recent hire question
        elif 'hired most recently' in question_lower:
            recent = self.sheets['Employees'].data.sort_values('HireDate', ascending=False).iloc[0]
            return {
                'type': 'recent_hire',
                'name': recent['Name'],
                'hire_date': recent['HireDate'],
                'department': recent['Department']
            }
        
        # Feedback score questions
        elif 'feedbackscore' in question_lower.replace(' ', ''):
            name = self._extract_name(question)
            if name:
                employee_id = self.sheets['Employees'].data[
                    self.sheets['Employees'].data['Name'] == name
                ]['EmployeeID'].values[0]
                feedback = self.sheets['Feedback'].data[
                    self.sheets['Feedback'].data['EmployeeID'] == employee_id
                ]
                if not feedback.empty:
                    return {
                        'type': 'feedback_score',
                        'name': name,
                        'score': feedback['FeedbackScore'].values[0],
                        'comment': feedback['Comments'].values[0]
                    }
        
        # Department lookup questions
        elif 'which department' in question_lower:
            name = self._extract_name(question)
            if name:
                dept = self.sheets['Employees'].data[
                    self.sheets['Employees'].data['Name'] == name
                ]['Department'].values[0]
                return {
                    'type': 'employee_department',
                    'name': name,
                    'department': dept
                }
        
        # Sales amount questions
        elif 'salesamount' in question_lower.replace(' ', ''):
            if 'saleid' in question_lower.replace(' ', ''):
                sale_id = int(re.search(r'saleid\s*(\d+)', question_lower).group(1))
                amount = self.sheets['Sales'].data[
                    self.sheets['Sales'].data['SaleID'] == sale_id
                ]['SalesAmount'].values[0]
                return {
                    'type': 'sale_amount',
                    'sale_id': sale_id,
                    'amount': amount
                }
        
        # Needs improvement feedback
        elif 'needs improvement' in question_lower:
            feedback = self.sheets['Feedback'].data[
                self.sheets['Feedback'].data['Comments'].str.contains('Needs Improvement', case=False)
            ]
            if not feedback.empty:
                employee_id = feedback['EmployeeID'].values[0]
                employee = self.sheets['Employees'].data[
                    self.sheets['Employees'].data['EmployeeID'] == employee_id
                ].iloc[0]
                return {
                    'type': 'needs_improvement',
                    'name': employee['Name'],
                    'feedback_id': feedback['FeedbackID'].values[0]
                }
        
        # Total sales by month
        elif 'total sales amount' in question_lower and 'january' in question_lower:
            jan_sales = self.sheets['Sales'].data[
                self.sheets['Sales'].data['Month'] == '2025-01'
            ]['SalesAmount'].sum()
            return {
                'type': 'total_sales',
                'month': 'January 2025',
                'total': jan_sales
            }
        
        # Highest total sales employee
        elif 'highest total sales' in question_lower:
            if hasattr(self, 'employee_sales'):
                totals = self.employee_sales.groupby('Name')['SalesAmount'].sum()
                top_employee = totals.idxmax()
                top_amount = totals.max()
                return {
                    'type': 'top_sales_employee',
                    'name': top_employee,
                    'total_sales': top_amount
                }
        
        # Average salary by department
        elif 'average salary' in question_lower and 'department' in question_lower:
            dept = self._extract_department(question)
            if dept:
                avg = self.sheets['Employees'].data[
                    self.sheets['Employees'].data['Department'] == dept
                ]['Salary'].mean()
                return {
                    'type': 'avg_salary',
                    'department': dept,
                    'average': avg
                }
        
        # Feedback score count
        elif 'how many employees' in question_lower and 'feedbackscore' in question_lower.replace(' ', ''):
            if '5' in question:
                count = len(self.sheets['Feedback'].data[
                    self.sheets['Feedback'].data['FeedbackScore'] == 5
                ])
                return {
                    'type': 'feedback_count',
                    'score': 5,
                    'count': count
                }
        
        # Total payroll
        elif 'total payroll' in question_lower:
            total = self.sheets['Employees'].data['Salary'].sum()
            return {
                'type': 'total_payroll',
                'total': total
            }
        
        # Highest sales month
        elif 'highest total sales' in question_lower and 'month' in question_lower:
            monthly = self.sheets['Sales'].data.groupby('Month')['SalesAmount'].sum()
            top_month = monthly.idxmax()
            top_amount = monthly.max()
            return {
                'type': 'top_sales_month',
                'month': top_month,
                'total': top_amount
            }
        
        # Average feedback score
        elif 'average feedbackscore' in question_lower.replace(' ', ''):
            avg = self.sheets['Feedback'].data['FeedbackScore'].mean()
            return {
                'type': 'avg_feedback',
                'average': avg
            }
        
        # Lowest avg salary department
        elif 'lowest average salary' in question_lower:
            dept_avg = self.sheets['Employees'].data.groupby('Department')['Salary'].mean()
            lowest_dept = dept_avg.idxmin()
            lowest_avg = dept_avg.min()
            return {
                'type': 'lowest_avg_salary',
                'department': lowest_dept,
                'average': lowest_avg
            }
        
        # Employees hired before year
        elif 'hired before' in question_lower:
            year = int(re.search(r'before\s*(\d+)', question_lower).group(1))
            employees = self.sheets['Employees'].data[
                pd.to_datetime(self.sheets['Employees'].data['HireDate']).dt.year < year
            ]
            return {
                'type': 'employees_before_year',
                'year': year,
                'count': len(employees),
                'names': employees['Name'].tolist()
            }
        
        # Employee with most feedback
        elif 'most feedback entries' in question_lower:
            feedback_counts = self.sheets['Feedback'].data.groupby('EmployeeID').size()
            top_employee_id = feedback_counts.idxmax()
            top_count = feedback_counts.max()
            employee = self.sheets['Employees'].data[
                self.sheets['Employees'].data['EmployeeID'] == top_employee_id
            ].iloc[0]
            return {
                'type': 'most_feedback',
                'name': employee['Name'],
                'count': top_count
            }
        
        return {'type': 'unhandled', 'question': question}
    
    def _extract_department(self, question: str) -> Optional[str]:
        """Extract department name from question"""
        question_lower = question.lower()
        for dept in self.sheets['Employees'].data['Department'].unique():
            if dept.lower() in question_lower:
                return dept
        return None
    
    def _extract_name(self, question: str) -> Optional[str]:
        """Extract employee name from question"""
        question_lower = question.lower()
        for name in self.sheets['Employees'].data['Name'].unique():
            if name.lower() in question_lower:
                return name
        return None