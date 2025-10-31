const { executeSql, TYPES } = require('../db');  
  
module.exports = async function (context, req) {  
  const refCode = req.query.ref || 'Direct';  
  
  try {  
    // Look up merchant by refCode  
    const merchants = await executeSql(  
      "SELECT MerchantID FROM Merchants WHERE RefCode = @refCode",  
      [{ name: 'refCode', type: TYPES.NVarChar, value: refCode }]  
    );  
  
    if (merchants.length > 0) {  
      await executeSql(  
        "INSERT INTO Scans (ReferringMerchantID) VALUES (@mid)",  
        [{ name: 'mid', type: TYPES.Int, value: merchants[0].MerchantID }]  
      );  
    }  
  
    // Fetch active offers  
    const offers = await executeSql(`  
      SELECT o.OfferID, m.Name AS Merchant, o.Description, o.CodePrefix  
      FROM Offers o  
      JOIN Merchants m ON o.MerchantID = m.MerchantID  
      WHERE o.Active = 1  
    `);  
  
    context.res = { status: 200, body: offers };  
  
  } catch (error) {  
    context.res = { status: 500, body: "Error: " + error.message };  
  }  
};