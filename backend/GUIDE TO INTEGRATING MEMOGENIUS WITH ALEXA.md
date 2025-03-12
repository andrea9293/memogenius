# GUIDE TO INTEGRATING MEMOGENIUS WITH ALEXA

This configuration is only for italian language but can be easily adapted to other languages.
## PART 1: CONFIGURING CLOUDFLARE TUNNEL (ON WINDOWS)

1. Install Cloudflared:
   - Using scoop: `scoop install cloudflared`

2. Authenticate with your Cloudflare account:
   ``` bash
   cloudflared tunnel login
   ```
   (This will open the browser for authentication)

3. Create a tunnel:
   ``` bash
   cloudflared tunnel create memogenius
   ```
   (Take note of the generated tunnel ID)

4. Create a config.yml file in the .cloudflared directory in your home directory (usually C:\Users\<username>\.cloudflared\config.yml):
   ``` yaml
   tunnel: <GENERATED-TUNNEL-ID>
   credentials-file: C:\Users\<username>\.cloudflared\<GENERATED-TUNNEL-ID>.json
   
   ingress:
     - hostname: memogenius.yourdomain.com
       service: http://localhost:8000
     - service: http_status:404
   ```

5. Configure DNS in the Cloudflare panel:
   - Go to Cloudflare Dashboard > Your domain > DNS
   - Add a CNAME record:
     - Name: memogenius (or the subdomain you prefer)
     - Target: <GENERATED-TUNNEL-ID>.cfargotunnel.com
     - Enable the proxy (orange icon)

6. Start the tunnel:
   ``` bash
   cloudflared tunnel run memogenius
   ```

7. (Optional) Install the tunnel as a Windows service:
   ``` bash
   cloudflared service install
   ```

## PART 2: CREATING THE ALEXA SKILL

1. Go to https://developer.amazon.com/alexa/console/ask and log in

2. Click on "Create Skill"

3. Set up the basic configurations:
   - Skill name: MemoGenius
   - Default language: Italian (or your preference)
   - Skill type: Custom
   - Hosting method: Provision your own
   - Choose a template: Start from scratch

4. Configure the interaction model with the following JSON:
   ``` json
   {
      "interactionModel": {
         "languageModel": {
               "invocationName": "memo genius",
               "intents": [
                  {
                     "name": "AMAZON.CancelIntent",
                     "samples": [
                           "cancella",
                           "esci",
                           "chiudi"
                     ]
                  },
                  {
                     "name": "AMAZON.HelpIntent",
                     "samples": [
                           "aiuto",
                           "aiutami",
                           "come funziona",
                           "cosa puoi fare"
                     ]
                  },
                  {
                     "name": "AMAZON.StopIntent",
                     "samples": [
                           "stop",
                           "annulla",
                           "basta",
                           "fermati",
                           "fine"
                     ]
                  },
                  {
                     "name": "AMAZON.NavigateHomeIntent",
                     "samples": []
                  },
                  {
                     "name": "AMAZON.FallbackIntent",
                     "samples": []
                  },
                  {
                     "name": "QueryIntent",
                     "slots": [
                           {
                              "name": "Message",
                              "type": "AMAZON.SearchQuery"
                           }
                     ],
                     "samples": [
                           "memo genius {Message}",
                           "memogenius {Message}",
                           "neko {Message}",
                           "neco {Message}",
                           "ricorda {Message}",
                           "aiutami con {Message}",
                           "per favore {Message}",
                           "esegui {Message}",
                           "ho bisogno di {Message}",
                           "vorrei {Message}",
                           "chiedi {Message}",
                           "dimmi {Message}",
                           "cerca {Message}",
                           "trova {Message}",
                           "mostrami {Message}",
                           "quando {Message}",
                           "cosa {Message}",
                           "come {Message}",
                           "chi {Message}",
                           "dove {Message}",
                           "perché {Message}",
                           "quale {Message}",
                           "dammi {Message}",
                           "voglio {Message}",
                           "avrei bisogno di {Message}",
                           "mi serve {Message}",
                           "posso {Message}",
                           "puoi {Message}",
                           "dovresti {Message}",
                           "potresti {Message}",
                           "è possibile {Message}",
                           "vorrei sapere {Message}",
                           "mi piacerebbe {Message}",
                           "{Message} per favore",
                           "{Message} grazie",
                           "per {Message}",
                           "con {Message}",
                           "informazioni su {Message}",
                           "dettagli su {Message}"
                     ]
                  }
               ],
               "types": []
         },
         "dialog": {
               "intents": [
                  {
                     "name": "QueryIntent",
                     "confirmationRequired": false,
                     "prompts": {},
                     "slots": [
                           {
                              "name": "Message",
                              "type": "AMAZON.SearchQuery",
                              "confirmationRequired": false,
                              "elicitationRequired": true,
                              "prompts": {
                                 "elicitation": "Elicit.Slot.Message"
                              }
                           }
                     ]
                  }
               ],
               "delegationStrategy": "ALWAYS"
         },
         "prompts": [
               {
                  "id": "Elicit.Slot.Message",
                  "variations": [
                     {
                           "type": "PlainText",
                           "value": "Cosa vuoi chiedere?"
                     },
                     {
                           "type": "PlainText",
                           "value": "Come posso aiutarti?"
                     },
                     {
                           "type": "PlainText",
                           "value": "Dimmi cosa ti serve."
                     }
                  ]
               }
         ]
      }
   }
   ```

5. Configure the endpoint:
   - Go to the "Endpoint" section
   - Select "HTTPS"
   - In the "Default Region" field, enter the complete URL of your server:
     `https://memogenius.yourdomain.com/alexa/intent`
   - For SSL, select: "My development endpoint is a sub-domain of a domain that has a wildcard certificate from a certificate authority"
   - Click on "Save Endpoints"

6. Go to "Invocation" and verify that the invocation name is set to "memo genius"

7. Save the model and click on "Build Model"

## PART 3: STARTUP AND TESTING

1. Start the MemoGenius application:
   ``` bash
   cd path\to\memogenius\backend
   python start_all.py
   ```

2. Make sure the Cloudflare tunnel is active:
   ``` bash
   cloudflared tunnel run memogenius
   ```

3. Test the skill:
   - Go to the "Test" section in the Alexa console
   - Enable testing for your skill
   - Use the invocation phrase "Alexa, open memo genius"
   - Test various interactions

## PART 4: TROUBLESHOOTING

1. If requests are not reaching the server:
   - Verify that cloudflared is running
   - Check cloudflared logs for errors
   - Verify that the URL in the Alexa endpoint is correct

2. If responses are too slow:
   - Remember that Alexa has an 8-second timeout
   - Consider optimizing API calls to Gemini

3. For issues with response formatting:
   - Verify that HTML cleaning is working correctly
   - Test with simpler responses

4. For user authentication problems:
   - Configure a system to associate Alexa users with your MemoGenius users
   - Use a database to map Alexa user IDs to your users

## PART 5: IMPROVEMENTS
Next steps:
   - Consider adding visual responses for Alexa devices with screens
   - Implement Account Linking for a personalized experience
   - Add more specific intents for advanced features
   - add dedicated agent to build response with alexa tags
