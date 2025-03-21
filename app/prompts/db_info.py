DB_INFO = {}

DB_INFO["TABLE_DESCRIPTION"] = {
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


DB_INFO["TABLE_TRANSACTIONS"] = {
    "table_schema": """[
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
    "description": "The source of the transaction, only two values: 支付宝 or 微信"
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
    "description": "The direction of the transaction, only two values: 收入 or 支出"
  },
  {
    "column_name": "ledger",
    "data_type": "text",
    "description": "Transaction ledger, Expenses:Food:Restaurant, Expenses:Shopping:Daily, ..."
  }
]""",
    "ledger_description": """[
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
]""",
}


DB_INFO["ABANDONED_TABLES"] = {
    "transactions_all": """[
  {
    "column_name": "id",
    "data_type": "integer"
  },
  {
    "column_name": "time",
    "data_type": "timestamp without time zone"
  },
  {
    "column_name": "source",
    "data_type": "text"
  },
  {
    "column_name": "target",
    "data_type": "text"
  },
  {
    "column_name": "description",
    "data_type": "text"
  },
  {
    "column_name": "direction",
    "data_type": "text"
  },
  {
    "column_name": "amount",
    "data_type": "numeric"
  },
  {
    "column_name": "status",
    "data_type": "text"
  },
  {
    "column_name": "type",
    "data_type": "text"
  },
  {
    "column_name": "memo",
    "data_type": "text"
  },
  {
    "column_name": "category",
    "data_type": "text"
  },
  {
    "column_name": "transaction_id",
    "data_type": "text"
  },
  {
    "column_name": "merchant_id",
    "data_type": "text"
  },
  {
    "column_name": "created_at",
    "data_type": "timestamp with time zone"
  }
  {
    "column_name": "ledger",
    "data_type": "text"
  }
]""",
}
