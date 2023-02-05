/**
 * Get all dealerships
 */

const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
  const { IAM_API_KEY, COUCH_URL, COUCH_DATABASE } = params

  const authenticator = new IamAuthenticator({ apikey: IAM_API_KEY })
  const cloudant = CloudantV1.newInstance({ authenticator: authenticator });
  cloudant.setServiceUrl(COUCH_URL);

  let selector = {};

  if (params.state) selector.state = { "$eq": params.state };

  let dealerList = (Object.keys(selector).length
    ? getMatchingRecords(cloudant, COUCH_DATABASE, selector)
    : getAllRecords(cloudant, COUCH_DATABASE));

  return dealerList;
}

function getAllRecords(cloudant, dbname) {
  return new Promise((resolve, reject) => {
    cloudant.postAllDocs({ db: dbname, includeDocs: true, limit: 10 })            
      .then((result)=>{ resolve({result: result.result.rows.map((row) => row.doc)}); })
      .catch(err => {
        console.log(err);
        reject({ err: err });
      });
    })
}

function getMatchingRecords(cloudant, dbname, selector) {
  return new Promise((resolve, reject) => {
    cloudant.postFind({ db: dbname, selector: selector })
      .then((result) => {
        resolve({result: result.result.docs});
      })
      .catch(err => {
        console.log(err);
        reject({err: err});
      });
  })
}
