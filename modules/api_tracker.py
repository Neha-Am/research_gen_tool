import json
import os
from datetime import datetime

class APITracker:
    """Tracks API calls and provides statistics"""
    
    def __init__(self):
        self.tracker_file = 'api_call_tracker.json'
    
    def load_api_call_count(self):
        """Load API call count from file"""
        try:
            if os.path.exists(self.tracker_file):
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                    return data.get('total_calls', 0), data.get('call_history', [])
            return 0, []
        except Exception as e:
            print(f"Error loading API call count: {str(e)}")
            return 0, []
    
    def save_api_call_count(self, total_calls, call_history):
        """Save API call count to file"""
        try:
            data = {
                'total_calls': total_calls,
                'call_history': call_history,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.tracker_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving API call count: {str(e)}")
    
    def increment_call(self, function_name):
        """Increment API call count and save to file"""
        # Load current count
        total_calls, call_history = self.load_api_call_count()
        
        # Increment count
        total_calls += 1
        
        # Add to history
        call_record = {
            'timestamp': datetime.now().isoformat(),
            'function': function_name,
            'call_number': total_calls
        }
        call_history.append(call_record)
        
        # Keep only last 100 records to prevent file from growing too large
        if len(call_history) > 100:
            call_history = call_history[-100:]
        
        # Save updated count
        self.save_api_call_count(total_calls, call_history)
        
        return total_calls
    
    def reset_stats(self):
        """Reset API call count to zero"""
        try:
            data = {
                'total_calls': 0,
                'call_history': [],
                'last_updated': datetime.now().isoformat(),
                'reset_at': datetime.now().isoformat()
            }
            with open(self.tracker_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error resetting API call count: {str(e)}")
            return False
    
    def get_stats(self):
        """Get comprehensive API usage statistics"""
        try:
            total_calls, call_history = self.load_api_call_count()
            
            # Calculate today's calls
            today_calls = 0
            if call_history:
                today_calls = len([call for call in call_history 
                                 if datetime.fromisoformat(call['timestamp']).date() == datetime.now().date()])
            
            # Calculate function breakdown
            function_breakdown = {}
            for call in call_history:
                func_name = call['function']
                if func_name not in function_breakdown:
                    function_breakdown[func_name] = 0
                function_breakdown[func_name] += 1
            
            # Calculate estimated cost (Gemini 2.0 Flash pricing as of 2024)
            # Input: $0.075 per 1M tokens, Output: $0.30 per 1M tokens
            # Assuming average of 2000 input tokens and 1000 output tokens per call
            estimated_input_tokens = total_calls * 2000
            estimated_output_tokens = total_calls * 1000
            estimated_cost_input = (estimated_input_tokens / 1000000) * 0.075
            estimated_cost_output = (estimated_output_tokens / 1000000) * 0.30
            estimated_total_cost = estimated_cost_input + estimated_cost_output
            
            # Get last call time
            last_call_time = None
            if call_history:
                last_call_time = call_history[-1]['timestamp']
            
            return {
                'summary': {
                    'total_calls': total_calls,
                    'today_calls': today_calls,
                    'last_call_time': last_call_time,
                    'last_updated': datetime.now().isoformat(),
                    'estimated_cost': {
                        'input_tokens': estimated_input_tokens,
                        'output_tokens': estimated_output_tokens,
                        'input_cost_usd': round(estimated_cost_input, 4),
                        'output_cost_usd': round(estimated_cost_output, 4),
                        'total_cost_usd': round(estimated_total_cost, 4)
                    }
                },
                'function_breakdown': function_breakdown,
                'recent_calls': call_history[-10:] if len(call_history) > 10 else call_history
            }
            
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {
                'error': str(e),
                'summary': {
                    'total_calls': 0,
                    'today_calls': 0,
                    'last_call_time': None,
                    'last_updated': datetime.now().isoformat(),
                    'estimated_cost': {
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'input_cost_usd': 0,
                        'output_cost_usd': 0,
                        'total_cost_usd': 0
                    }
                },
                'function_breakdown': {},
                'recent_calls': []
            }
    
    def export_stats_csv(self):
        """Export API call history as CSV"""
        try:
            _, call_history = self.load_api_call_count()
            
            csv_data = "Call Number,Function,Timestamp,Date,Time\n"
            for call in call_history:
                call_time = datetime.fromisoformat(call['timestamp'])
                csv_data += f"{call['call_number']},{call['function']},{call['timestamp']},{call_time.strftime('%Y-%m-%d')},{call_time.strftime('%H:%M:%S')}\n"
            
            return csv_data
        except Exception as e:
            print(f"Error exporting CSV: {str(e)}")
            return ""
    
    def export_stats_text(self):
        """Export API call history as text report"""
        try:
            stats = self.get_stats()
            
            report = f"""API Call Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TOTAL API CALLS: {stats['summary']['total_calls']}
TODAY'S CALLS: {stats['summary']['today_calls']}
LAST CALL: {stats['summary']['last_call_time']}

COST ESTIMATION:
- Estimated Input Tokens: {stats['summary']['estimated_cost']['input_tokens']:,}
- Estimated Output Tokens: {stats['summary']['estimated_cost']['output_tokens']:,}
- Input Cost: ${stats['summary']['estimated_cost']['input_cost_usd']}
- Output Cost: ${stats['summary']['estimated_cost']['output_cost_usd']}
- Total Estimated Cost: ${stats['summary']['estimated_cost']['total_cost_usd']}

FUNCTION BREAKDOWN:
"""
            for func, count in stats['function_breakdown'].items():
                report += f"- {func}: {count} calls\n"
            
            report += f"\nDETAILED HISTORY (Last 20 calls):\n"
            report += "="*50 + "\n"
            for call in stats['recent_calls'][-20:]:
                call_time = datetime.fromisoformat(call['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                report += f"#{call['call_number']} - {call['function']} - {call_time}\n"
            
            return report
        except Exception as e:
            print(f"Error exporting text report: {str(e)}")
            return f"Error generating report: {str(e)}" 