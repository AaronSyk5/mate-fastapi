from chatbot.conexion_supabase import supabase

def obtener_clientes_activos(empresa_id):
    response = supabase.table("clientes_crm").select("*").eq("empresa_id", empresa_id).eq("activo", True).execute()
    return response.data

# Prueba directa
if __name__ == "__main__":
    empresa_id = "empresa_001"  # Usa el ID real de una empresa en tu base
    clientes = obtener_clientes_activos(empresa_id)

    print(f"Clientes activos para {empresa_id}:")
    for cliente in clientes:
        print(f"- {cliente['nombre']} (ID: {cliente['id']})")
