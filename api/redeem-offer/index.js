const { executeSql, TYPES } = require('../db');  
  
module.exports = async function (context, req) {  
  const { offerId, refCode } = req.body || {};  
  
  if (!offerId) {  
    context.res = { status: 400, body: "Missing offerId" };  
    return;  
  }  
  
  try {  
    let referringMerchantID = null;  
  
    if (refCode) {  
      const merchants = await executeSql(  
        "SELECT MerchantID FROM Merchants WHERE RefCode = @refCode",  
        [{ name: 'refCode', type: TYPES.NVarChar, value: refCode }]  
      );  
      if (merchants.length > 0) {  
        referringMerchantID = merchants[0].MerchantID;  
      }  
    }  
  
    await executeSql(  
      "INSERT INTO Redemptions (OfferID, ReferringMerchantID) VALUES (@offerId, @mid)",  
      [  
        { name: 'offerId', type: TYPES.Int, value: parseInt(offerId) },  
        { name: 'mid', type: TYPES.Int, value: referringMerchantID }  
      ]  
    );  
  
    context.res = { status: 200, body: { message: "Offer redeemed" } };  
  
  } catch (error) {  
    context.res = { status: 500, body: "Error: " + error.message };  
  }  
};