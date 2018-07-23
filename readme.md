## Files

0. `sku_{attr,info,prom,prom_testing,quantile,sales}.csv`	赛题所给文件
1. `features[0-9].csv`	不用git同步，共`1000*6*762`个sample，每个39维features和1维label(0-quantity那一列)
2. `stat.csv`	均值方差（没用这个）
3. `stdvar.csv`	每个(sku,dc）14维，分别为dc全年,dc1-12月,sku全年的stdvar
4. `test.csv`	预测结果（可以直接提交）
5. `model.py`	Machine Learning脚本
6. `processing.py`	提特征脚本
7. `test.py`	不用理

## features

- sku_id,dc_id,date
- -x_quantity			`第(now-x)天quantity`
- -x_vendibility		`第(now-x)vendibility`

(共k0天)

- original_price		`原价，当天无记录则为该sku平均原价`
- discount			`标价/原价，0.0-1.0，当天无记录则为1`
- prom_sku			`有promotion_type的时候该sku销量总和/该sku销量总和，理论上应该>1`
- prom_cate3			`有promotion_type的时候该第三类别销量总和/该第三类别销量总和，理论上应该>1`
- k1days-avr-discount	`前k1天平均discount`
- k1days-avr-quantity	`前k1天平均quantity`
- k2days-avr-discount,k2days-avr-quantity
month-avr-quantity-first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc
`所属first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc对在该月的平均quantity`
- weekday-avr-quantity-first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc
`所属first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc对在星期x的平均quantity`
