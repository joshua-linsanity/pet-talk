## Introducing Pet-Talks! 🐰🥕💬
### Inspiration
Instead of having a one-sided conversation, imagine having a conversation with your pet, where they speak in human words. Your Disney princess dreams can finally come true! Introducing Pet Talks: have conversations with your pet by detecting gestures, movements, and even sounds. Pet Talks can also detect unusual behavior/gestures that can quickly detect medical problems.
As bunny owners, we find ourselves talking to our bunny every day as if she were a human. Our pets are emotional and sophisticated creatures, and we are always striving to connect with our pets in any way possible. Have you ever looked at your pet and asked yourself: what is going on inside their head? What if… we can vocalize those emotions? Instead of having a one-sided conversation, imagine having a conversation with your pet, where they speak in human words. 

### What it does
Introducing Pet Talks, a pet cam that allows you to have conversations with your pet by detecting gestures, movements, and even sounds. Pet Talks can also detect unusual behavior or gestures that can quickly detect medical problems.GI stasis is a common and potentially fatal condition affecting thousands of rabbits daily. Detecting its early signs can be challenging, as changes in their behavior and eating habits often go unnoticed when they're out of sight.
"Pet Talks – Because every hop, twitch, and nibble has a story to tell!"
### How we built it
We started implementing a desktop version, which uses our phone as the webcam and our laptop as the chat tool.
The webcam takes short videos or bursts of photos every time we start typing, and hit enter. Those photos are then fed through the LLM model configured, which generates a medical response or simply a live status update for the bunny. 
### Challenges we ran into
We initially attempted to use the Meta Oculus to implement a live video feed from the webcam. However, the Oculus had many issues starting up the wireless connection.
Also, at first, we asked Gemini to interact with the user as if it were a rabbit, which posed a challenge as the responses seemed too mindless and lacked reliable information. We would prompt, “Are you healthy?” and the bunny would respond, “I am just a cute fluffy bunny. Give me carrots!” This provided no valid information on her health or actions. 
### Accomplishments that we're proud of
We began tailoring Gemini to give a more accurate response through better instructions and some anti-jail break methods. However, we were also able to utilize multiple LLM solutions such as Gemini, PerplexityAI, and OpenAI’s models, hinting at a future where the user experience is fully customizable. 
The perplexity API call that we set up to be tailored is really nice since we can gather a detailed report with minimal effort.
###  What we learned
We learned that LLMs are difficult to effectively finetune, which is why we need to make use of the existing sponsor resources provided to us. We need a balance between cool technology and what is already familiar; since we didn’t want to be focusing too much on making use of technology, but rather let the passion in our idea make itself known.
The presentation is also equally as crucial in our project since that is our user’s first impression, and not all group members have experience DEMOing so we are very thrilled to be able to have fun during this technical challenge.
### What's Next for Pet Talks
With more time, we plan to create an iOS version in which users can have better accessibility when viewing real-time footage from a remote location. The IOS app will be paired with a 360 camera system with AI detection,  geofencing, and of course, the chat and pet translation feature, and the health check as well. The app will alert users wherever unusual activity occurs, such as when the bunny hasn't been eating for the past 3 hours, the user will be alerted and if this goes on for more than 12, the user will get a GI status alert and description, the user can choose to automatically send the message to their local vet, and book a vet appointment if severe. We also plan to do text-to-speech, and users can hear their pet speak in unique voices.
