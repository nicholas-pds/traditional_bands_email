  SELECT
    COUNT(DISTINCT CASE WHEN cll.[Description] = 'Design Cart'        THEN ca.CaseNumber END) AS [Design Cart],
    COUNT(DISTINCT CASE WHEN cll.[Description] = '3D Design'          THEN ca.CaseNumber END) AS [3D Design],
    COUNT(DISTINCT CASE WHEN cll.[Description] = '3D Manufacturing'   THEN ca.CaseNumber END) AS [3D Manufacturing],
    COUNT(DISTINCT CASE WHEN cll.[Description] = 'Metal Shelf'        THEN ca.CaseNumber END) AS [Metal Shelf],
    COUNT(DISTINCT CASE WHEN cll.[Description] = 'Banding'            THEN ca.CaseNumber END) AS [Banding Station],
    
    -- Total: sum of all 5 location counts
    COUNT(DISTINCT CASE WHEN cll.[Description] IN ('Metal Shelf', '3D Design', '3D Manufacturing', 'Design Cart', 'Banding') 
                        THEN ca.CaseNumber END) AS [Total]
FROM dbo.Cases AS ca
INNER JOIN dbo.CaseTasks AS ct
    ON ct.CaseID = ca.CaseID
LEFT JOIN dbo.CaseLogLocations AS cll
    ON ca.LastLocationID = cll.ID
    AND cll.[Description] IN ('Metal Shelf', '3D Design', '3D Manufacturing', 'Design Cart', 'Banding')
WHERE ct.Task = 'band'
  AND ct.CompleteDate IS NULL
  AND ca.Status = 'In Production';