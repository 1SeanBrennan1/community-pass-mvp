const { Connection, Request, TYPES } = require('tedious');  
  
const config = {  
  server: process.env.SQL_SERVER,  
  authentication: {  
    type: 'default',  
    options: {  
      userName: process.env.SQL_USER,  
      password: process.env.SQL_PASSWORD  
    }  
  },  
  options: {  
    encrypt: true,  
    database: process.env.SQL_DB  
  }  
};  
  
function executeSql(query, params = []) {  
  return new Promise((resolve, reject) => {  
    const connection = new Connection(config);  
  
    connection.on('connect', err => {  
      if (err) return reject(err);  
  
      const request = new Request(query, (err, rowCount, rows) => {  
        if (err) return reject(err);  
  
        const result = rows.map(row => {  
          let obj = {};  
          row.forEach(col => { obj[col.metadata.colName] = col.value; });  
          return obj;  
        });  
        resolve(result);  
        connection.close();  
      });  
  
      params.forEach(p => request.addParameter(p.name, p.type, p.value));  
      connection.execSql(request);  
    });  
  });  
}  
  
module.exports = { executeSql, TYPES };