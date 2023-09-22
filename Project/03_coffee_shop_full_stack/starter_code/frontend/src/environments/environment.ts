export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-jnctgyygu6mx3zfm.us', // the auth0 domain prefix
    audience: 'caffee', // the audience set for the auth0 app
    clientId: 'Pz3MMDhTZWSRyhqOGR4XapGYvAsWgcXu', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:4200', // the base url of the running ionic application. 
  }
};
