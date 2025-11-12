SELECT
    CAST(ca.ShipDate AS DATE)                                            AS ShipDate,

    /* Total for all locations (your original column) */
    COUNT(DISTINCT ca.CaseNumber)                                        AS AllLocations,

    /* One column per location – only cases whose LAST location matches */
	COUNT(DISTINCT CASE WHEN cll.[Description] = 'Design Cart'        THEN ca.CaseNumber END) AS [DesignCart],
    COUNT(DISTINCT CASE WHEN cll.[Description] = '3D Design'          THEN ca.CaseNumber END) AS [3DDesign],
    COUNT(DISTINCT CASE WHEN cll.[Description] = '3D Manufacturing'   THEN ca.CaseNumber END) AS [3DManufacturing],
	    COUNT(DISTINCT CASE WHEN cll.[Description] = 'Metal Shelf'        THEN ca.CaseNumber END) AS [MetalShelf]


FROM dbo.Cases AS ca
INNER JOIN dbo.CaseTasks AS ct
        ON ct.CaseID = ca.CaseID
LEFT  JOIN dbo.CaseLogLocations AS cll
        ON ca.LastLocationID = cll.ID
       AND cll.[Description] IN ('Metal Shelf', '3D Design', '3D Manufacturing', 'Design Cart')

WHERE ct.Task = 'band'
  AND ct.CompleteDate IS NULL
  AND ca.ShipDate >= DATEADD(DAY, -1, CAST(GETDATE() AS DATE))   -- from yesterday
  AND ca.ShipDate <  DATEADD(DAY, 14, CAST(GETDATE() AS DATE))   -- up to (but not including) +14 days

GROUP BY CAST(ca.ShipDate AS DATE)
ORDER BY ShipDate;