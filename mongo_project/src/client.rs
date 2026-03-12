use mongo::bson::doc;
use mongo::options{ ClientOptions, ServerApi, ServerApiVersion };
use mongo::Client;


pub async fn connect_to_mongo(uri: &str) -> mongo::error::Result<()> {
    let mut client_options = ClientOptions::parse(uri).await?;
}
