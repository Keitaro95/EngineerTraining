
下に行くほど詳細
本当は Level1に行くに従って下に書く


Level 1: Order (注文ルート) - 顧客情報、決済概要、メタデータ。
Level 2: Shipment (配送単位) - 配送業者、追跡番号、配送先住所。
Level 3: FulfillmentGroup (在庫拠点) - 特定の倉庫や店舗からの出荷指示。
Level 4: LineItem (商品明細) - SKU、単価、数量、適用割引。
Level 5: Component/Customization (構成要素) - セット商品の内訳、名入れ、ギフト包装等の属性。



from typing import List, Optional, Dict, Literal
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict, field_validator


```py
class OrderDetail(BaseModel):
    """
    第1階層：APIが受け取るJSONのルートオブジェクト
    """
    order_id:str = Field(..., description="注文ID")
    customer_id: str
    customer_email: EmailStr
    order_date: datetime = Field(default_factory=datetime.now)
    status: str = "created"
    shipments: List[Shipment] # ここはリスト
    tags: Dict[str, str] = Field(default_factory=dict)

    # schemaをカスタマイズ
    # OpenAPI 仕様書 (openapi.json) にも example として出力される
    model_config = ConfigDict(
    json_schema_extra = {
        "example": {
            "order_id": "ORD-2025-001",
            "customer_id": "CUST-999",
            "customer_email": "user@example.com",
            "order_date": "2026-04-12T10:00:00",
            "status": "created",
            "shipments": [
                {
                    "shipment_id": "c0a8012e-1234-5678-9abc-def012345678",
                    "carrier_code": "YAMATO",
                    "tracking_number": "1234-5678-9012",
                    "shipping_address_id": "ADDR-001",
                    "fulfillment_groups": [
                        {
                            "warehouse_id": "WH-TOKYO-01",
                            "priority": 1,
                            "expected_ship_date": "2026-04-13T09:00:00",
                            "line_items": [
                                {
                                    "sku": "PC-DELL-XPS15",
                                    "product_name": "Dell XPS 15",
                                    "quantity": 1,
                                    "unit_price": 250000.0,
                                    "currency": "JPY",
                                    "components": [
                                        {
                                            "component_id": "CMP-001",
                                            "component_type": "material",
                                            "value": "16GB",
                                            "additional_cost": 0.0
                                        },
                                        {
                                            "component_id": "CMP-002",
                                            "component_type": "engraving",
                                            "value": "Happy Birthday",
                                            "additional_cost": 1500.0
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            "tags": {"campaign": "spring2026"}
        }
    }
)



# --- Level 2: Shipment (配送) ---
class Shipment(BaseModel):
    """
    第2階層：物理的な配送単位
    """
    shipment_id: UUID = Field(default_factory=uuid4)
    carrier_code: str = Field(..., description="配送業者コード (e.g., YAMATO, SAGAWA)")
    tracking_number: Optional[str] = None
    shipping_address_id: str
    
    # ネストされた第3階層のリスト
    fulfillment_groups: List[FulfillmentGroup]


# --- Level 3: Fulfillment Group (フルフィルメントグループ) ---
class FulfillmentGroup(BaseModel):
    """
    第3階層：論理的な在庫引き当て単位（倉庫や店舗）
    """
    warehouse_id: str
    priority: int = Field(default=1, ge=1, le=5)
    expected_ship_date: Optional[datetime] = None
    
    # ネストされた第4階層のリスト
    line_items: List[OrderLineItem]


# --- Level 4: Line Item (注文明細) ---
class OrderLineItem(BaseModel):
    """
    第4階層：具体的な注文商品
    """
    sku: str = Field(..., min_length=3, max_length=50, description="Stock Keeping Unit")
    product_name: str
    quantity: int = Field(..., gt=0, description="注文数量（1以上）")
    unit_price: float = Field(..., ge=0.0, description="単価")
    currency: str = Field(default="JPY", pattern=r"^[A-Z]{3}$")
    
    # ネストされた第5階層のリスト
    components: List[OrderComponent] = Field(default_factory=list)

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if v not in:
            raise ValueError('サポートされていない通貨コードです')
        return v
    

# --- Level 5: Component / Customization (構成要素・カスタマイズ) ---
class OrderComponent(BaseModel):
    """
    第5階層：商品の構成要素やカスタマイズ詳細
    例：PCのメモリ選定、指輪の刻印メッセージなど
    """
    component_id: str = Field(..., description="構成要素の一意なID", min_length=1)
    component_type: Literal['material', 'engraving', 'addon'] = Field(..., description="構成タイプ")
    value: str = Field(..., description="選択された値（例：'16GB', 'Happy Birthday'）")
    additional_cost: float = Field(default=0.0, ge=0.0, description="追加料金")

    model_config = ConfigDict(
        populate_by_name=True,
        extra='ignore'  # 将来的なフィールド追加に備え、未知のフィールドは無視する
    )
```



# frontend json
model_config の json_schema_extra.example OpenAPI がそのまま OpenAPI仕様書になるのか？

## Orbal自動生成
PydanticのmodelがそのままTSのIFになる
```ts
// 5階層がそのままネスト型になる
export interface OrderDetail {
  order_id: string;
  customer_id: string;
  customer_email: string;
  order_date: string;        // datetime → ISO string
  status: string;
  shipments: Shipment[];
  tags: Record<string, string>;
}

export interface Shipment {
  shipment_id: string;       // UUID → string
  carrier_code: string;
  tracking_number?: string;  // Optional → ? フィールド
  shipping_address_id: string;
  fulfillment_groups: FulfillmentGroup[];
}

export type OrderComponentComponentType = 
  'material' | 'engraving' | 'addon'; // Literal → union type

export interface OrderComponent {
  component_id: string;
  component_type: OrderComponentComponentType;
  value: string;
  additional_cost: number;
}
```
以下略

* TanStack Query hooks (src/api/generated/)
// 生成されるフック例
export const useGetOrder = (orderId: string) =>
  useQuery({
    queryKey: ['order', orderId],
    queryFn: () => getOrder(orderId),  // 型: () => Promise<OrderDetail>
  });

* MSW mock (src/mocks/)
// openapi.json の example がそのままレスポンスになる
http.get('/orders/:id', () =>
  HttpResponse.json({
    order_id: 'ORD-2025-001',
    shipments: [ ... ] // json_schema_extra の example が使われる
  })
)


**ネストを取り出す方法：flatMapで階層が深いものも、軽く取り出せる!!!**
```ts
import { useGetOrder } from '@/api/generated';
import type { OrderDetail, OrderLineItem } from '@/api/generated/model';

// UI専用のフラットな型（5階層 → 1階層に）
欲しいものをフラットに書きます

export interface FlatLineItem {
  sku: string;              // 第4層 OrderLineItem
  productName: string;      // 第4層 OrderLineItem
  quantity: number;         // 第4層 OrderLineItem
  unitPrice: number;        // 第4層 OrderLineItem
  warehouseId: string;      // 第3層 FulfillmentGroupから引き上げ
  shipmentId: string;       // 第2層 Shipmentから引き上げ
  engravingText?: string;   // 第5層 OrderComponentから引き上げ
}

// データ整形ロジック
function flattenLineItems(order: OrderDetail): FlatLineItem[] {
  // shipmentの中身をflatMap。階層を掘り下げて取り出せる超便利メソッド

  // shipment　= > から　の中のfulfillment_groupsを展開
  // さらに　fulfillment_groups をflatMapして　変数fg => fg.line_itemsとしてこの階層も展開

  つまり結局、階層をいくところまで遡って、最終的には itemで取り出してるってことですね！！！
  return order.shipments.flatMap(shipment =>
    shipment.fulfillment_groups.flatMap(fg =>
      fg.line_items.map(item => ({
        sku: item.sku,
        productName: item.product_name,
        quantity: item.quantity,
        unitPrice: item.unit_price,
        warehouseId: fg.warehouse_id,
        shipmentId: String(shipment.shipment_id),
        engravingText: item.components
          .find(c => c.component_type === 'engraving')?.value,
      }))
    )
  );
}

```

order                          ← 引数で受け取る（Lv1）
  └─ .shipments.flatMap(shipment =>    ← Lv2を展開、変数に束縛
       └─ .fulfillment_groups.flatMap(fg =>  ← Lv3を展開、変数に束縛
            └─ .line_items.map(item => ({    ← Lv4、ここが「目的地」
                 //
                 // ここで全階層の変数が使える！
                 //
                 sku:          item.sku,           // item（Lv4）
                 warehouseId:  fg.warehouse_id,    // fg（Lv3）
                 shipmentId:   shipment.shipment_id // shipment（Lv2）
               }))
          )
     )






