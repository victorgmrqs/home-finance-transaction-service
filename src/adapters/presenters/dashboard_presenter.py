"""
Dashboard Presenter
Formatação de respostas do dashboard
"""


def present_dashboard_summary(data: dict):
    """
    Formata resposta do dashboard summary

    Args:
        data: dict com resumo, categorias, paineis e estatisticas

    Returns:
        dict formatado para resposta da API
    """
    return {
        "code": "DASHBOARD_SUMMARY_SUCCESS",
        "message": "Dashboard summary retrieved successfully",
        "data": data
    }
