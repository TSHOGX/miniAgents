DB_INFO = {}


DB_INFO[
    "DB_INFO"
] = """Supabase database contain one table:

Table name: transactions
Table description: contains all the transactions
"""


DB_INFO["TABLE_SCHEMA"] = {
    "transactions": """[
  {
    "column_name": "id",
    "data_type": "integer",
    "description": "The unique identifier for the transaction"
  },
  {
    "column_name": "time",
    "data_type": "timestamp without time zone",
    "description": "The timestamp of the transaction"
  },
  {
    "column_name": "source",
    "data_type": "text",
    "description": "The source of the transaction, 支付宝 or 微信"
  },
  {
    "column_name": "amount",
    "data_type": "numeric",
    "description": "The amount of the transaction"
  },
  {
    "column_name": "description",
    "data_type": "text",
    "description": "The description of the transaction"
  },
  {
    "column_name": "direction",
    "data_type": "text",
    "description": "The direction of the transaction, 收入 or 支出"
  },
  {
    "column_name": "ledger",
    "data_type": "text",
    "description": "Transaction ledger, Expenses:Food:Restaurant, Expenses:Shopping:Daily, ..."
  }
]"""
}


DB_INFO[
    "HELPER_INFO"
] = """ledger_description 包含如下分类: [
  # 基本消费
  "Expenses:Food:Grocery",
  "Expenses:Food:Restaurant",
  "Expenses:Food:Delivery",
  "Expenses:Food:Cafeteria",
  # 交通出行
  "Expenses:Transportation:Taxi",
  "Expenses:Transportation:PublicTransit",
  "Expenses:Transportation:Train",
  "Expenses:Transportation:Airplane",
  # 购物消费
  "Expenses:Shopping:Clothing",
  "Expenses:Shopping:Electronics",
  "Expenses:Shopping:Daily",
  "Expenses:Shopping:Gift",
  # 生活服务
  "Expenses:Utility:Rent",
  "Expenses:Utility:Telecom",
  "Expenses:Utility:Water",
  "Expenses:Utility:Electricity",
  "Expenses:Utility:Gas",
  # 健康医疗
  "Expenses:Health:Medical",
  "Expenses:Health:Fitness",
  "Expenses:Health:Insurance",
  # 教育娱乐
  "Expenses:Education:Tuition",
  "Expenses:Education:Books",
  "Expenses:Education:Course",
  "Expenses:Entertainment",
  # 金融服务
  "Expenses:Financial:Fee",
  "Expenses:Financial:Interest",
  "Expenses:Financial:Investment",
  # 政府相关
  "Expenses:Government:Tax",
  "Expenses:Government:Social",
  # 其他
  "Expenses:Miscellaneous"
]"""
