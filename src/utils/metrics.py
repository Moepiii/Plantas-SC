import json
import os
from datetime import datetime, date
from collections import defaultdict

class BotMetrics:
    def __init__(self, metrics_file="data/metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = {
            "commands_usage": defaultdict(int),
            "daily_active_users": defaultdict(set),
            "total_users": set(),
            "errors": []
        }
        self.load_metrics()
    
    def load_metrics(self):
        """Carga métricas desde archivo"""
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            if "daily_active_users" in loaded_data:
                self.metrics["daily_active_users"] = defaultdict(set)
                for date_str, users in loaded_data["daily_active_users"].items():
                    self.metrics["daily_active_users"][date_str] = set(users)
            
            if "total_users" in loaded_data:
                self.metrics["total_users"] = set(loaded_data["total_users"])
                
        except Exception as e:
            self.metrics = {
                "commands_usage": defaultdict(int),
                "daily_active_users": defaultdict(set),
                "total_users": set(),
                "errors": []
            }
    
    def save_metrics(self):
        """Guarda métricas en archivo"""
        # Convertir sets a listas para JSON
        metrics_to_save = {
            "commands_usage": dict(self.metrics["commands_usage"]),
            "daily_active_users": {k: list(v) for k, v in self.metrics["daily_active_users"].items()},
            "errors": self.metrics["errors"],
            "total_users": list(self.metrics["total_users"])
        }
        
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_to_save, f, indent=2, ensure_ascii=False)
    
    def record_command_usage(self, user_id, command):
        """Registra el uso de un comando"""
        today = date.today().isoformat()
        self.metrics["commands_usage"][command] += 1
        self.metrics["daily_active_users"][today].add(user_id)
        self.metrics["total_users"].add(user_id)
        self.save_metrics()
    
    def record_error(self, user_id, command, error_msg):
        """Registra un error"""
        self.metrics["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "command": command,
            "error": error_msg
        })
        self.save_metrics()
    
    def get_usage_report(self):
        """Genera reporte de uso"""
        total_commands = sum(self.metrics["commands_usage"].values())
        total_users = len(self.metrics["total_users"])
        
        report = f"""
📊 **REPORTE DE USO DEL BOT**

👥 **Usuarios:**
- Total de usuarios: {total_users}
- Usuarios activos hoy: {len(self.metrics["daily_active_users"].get(date.today().isoformat(), []))}

🔧 **Comandos más usados:**
"""
        
        sorted_commands = sorted(
            self.metrics["commands_usage"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for command, count in sorted_commands[:10]:
            percentage = (count / total_commands * 100) if total_commands > 0 else 0
            report += f"- {command}: {count} veces ({percentage:.1f}%)\n"
        
        recent_errors = [e for e in self.metrics["errors"] 
                        if datetime.fromisoformat(e["timestamp"]).date() == date.today()]
        
        report += f"\n❌ **Errores hoy:** {len(recent_errors)}"
        
        return report

# Instancia global de métricas
bot_metrics = BotMetrics()