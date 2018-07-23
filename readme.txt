sku_id,dc_id,date
-x_quantity			第(now-x)天quantity
-x_vendibility		第(now-x)vendibility
(共k0天)
original_price		原价，当天无记录则为该sku平均原价
discount			标价/原价，0.0-1.0，当天无记录则为1
prom_sku			有promotion_type的时候该sku销量总和/该sku销量总和，理论上应该>1
prom_cate3			有promotion_type的时候该第三类别销量总和/该第三类别销量总和，理论上应该>1
k1days-avr-discount	前k1天平均discount
k1days-avr-quantity	前k1天平均quantity
k2days-avr-discount,k2days-avr-quantity
month-avr-quantity-first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc
所属first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc对在该月的平均quantity
weekday-avr-quantity-first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc
所属first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc对在星期x的平均quantity
