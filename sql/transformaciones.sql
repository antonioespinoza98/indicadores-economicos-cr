
create VIEW curado_sch.mrt_cuenta_ind AS
WITH mrt_cuenta_ind_cte AS (
    SELECT DISTINCT dim.nombre_indicador
    FROM curado_sch.fct_indicador AS fct
    LEFT JOIN curado_sch.dim_indicador AS dim
        ON fct.indicador_key = dim.indicador_key
)
SELECT *
FROM mrt_cuenta_ind_cte
ORDER BY nombre_indicador DESC;

create view curado_sch.mrt_indicadores_disp as
with mrt_indicadores_disp_cte AS(
	SELECT 
	    dim.codigo_indicador AS "Código de indicador",
	    dim.nombre_indicador AS "Nombre de indicador",
	    dim.descripcion_indicador AS "Descripción de indicador",
	    dim.periodicidad AS "Periodicidad",
	    fct.valorind AS "Valor de Indicador",
	    d.fecha AS "Fecha de emisión"
	    FROM curado_sch.fct_indicador fct  
	    LEFT JOIN curado_sch.dim_indicador dim 
	        ON fct.indicador_key = dim.indicador_key
	    LEFT JOIN curado_sch.dim_fecha d 
	        ON fct.date_key = d.date_key
)
select *
from mrt_indicadores_disp_cte
order by "Código de indicador";
