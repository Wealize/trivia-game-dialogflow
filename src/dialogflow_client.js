"use strict";

const dialogflow = require("dialogflow");
const intentsClient = new dialogflow.IntentsClient();
const contextsClient = new dialogflow.ContextsClient();
const projectAgentPath = intentsClient.projectAgentPath(projectId);
const INTENT_PARENT = "GAME";

async function sync(intents) {
  deleteIntents(INTENT_PARENT);
  createIntents(intents, INTENT_PARENT);
}

async function deleteIntents(INTENT_PARENT) {
  const intents = await listIntents();

  for (intent in intents) {
    if (intent.inputContextNames.contains(INTENT_PARENT)) {
      deleteIntent(projectId, intent.id);
    }
  }
}

async function createIntents(intents) {
  for (intent in intents) {
    createIntentForQuestion(intent);
  }
}

async function createIntentForQuestion(intent) {
    const question = intent[0];
    const correct_response = intent[1].concat(' ', intent[2]);
    const intent_name = slugify(question)

    if (intent_name) {
//         contexts = [{output_contexts_question}]
//  [('output_contexts_question', [ self.get_context(self.intent_parent + "-yes-followup", 2),
//             self.get_context(intent_name+"-followup", 2)]),
//         ('input_contexts_question', [self.get_context_path(self.intent_parent)]),
//         ('input_contexts_response', [self.get_context_path(self.intent_parent + "-yes-followup")])
//         ])
    }
}

async function slugify(text)
{
  return text.toString().toLowerCase()
    .replace(/\s+/g, '-')           // Replace spaces with -
    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
    .replace(/\-\-+/g, '-')         // Replace multiple - with single -
    .replace(/^-+/, '')             // Trim - from start of text
    .replace(/-+$/, '');            // Trim - from end of text
}

async function createIntents() {}

async function listIntents() {
  const request = {
    parent: projectAgentPath
  };

  console.log(projectAgentPath);

  // Send the request for listing intents.
  const [response] = await intentsClient.listIntents(request);
  response.forEach(intent => {
    console.log("====================");
    console.log(`Intent name: ${intent.name}`);
    console.log(`Intent display name: ${intent.displayName}`);
    console.log(`Action: ${intent.action}`);
    console.log(`Root folowup intent: ${intent.rootFollowupIntentName}`);
    console.log(`Parent followup intent: ${intent.parentFollowupIntentName}`);

    console.log("Input contexts:");
    intent.inputContextNames.forEach(inputContextName => {
      console.log(`\tName: ${inputContextName}`);
    });

    console.log("Output contexts:");
    intent.outputContexts.forEach(outputContext => {
      console.log(`\tName: ${outputContext.name}`);
    });
  });
}

async function createIntent(displayName, trainingPhrasesParts, messageTexts) {
  const trainingPhrases = [];

  trainingPhrasesParts.forEach(trainingPhrasesPart => {
    const part = {
      text: trainingPhrasesPart
    };

    const trainingPhrase = {
      type: "EXAMPLE",
      parts: [part]
    };

    trainingPhrases.push(trainingPhrase);
  });

  const messageText = {
    text: messageTexts
  };

  const message = {
    text: messageText
  };

  const intent = {
    displayName: displayName,
    trainingPhrases: trainingPhrases,
    messages: [message]
  };

  const createIntentRequest = {
    parent: agentPath,
    intent: intent
  };

  const responses = await intentsClient.createIntent(createIntentRequest);

  return responses;
}

async function deleteIntent(projectId, intentId) {
  const intentsClient = new dialogflow.IntentsClient();
  const intentPath = intentsClient.intentPath(projectId, intentId);
  const request = { name: intentPath };

  //   const result = await intentsClient.deleteIntent(request);

  return result;
}

async function listContexts(projectId, sessionId) {
  const sessionPath = contextsClient.sessionPath(projectId, sessionId);

  const request = {
    parent: sessionPath
  };

  const [response] = await contextsClient.listContexts(request);
  response.forEach(context => {
    console.log(`Context name: ${context.name}`);
    console.log(`Lifespan count: ${context.lifespanCount}`);
    console.log("Fields:");
    if (context.parameters !== null) {
      context.parameters.fields.forEach(field => {
        console.log(`\t${field.field}: ${field.value}`);
      });
    }
  });
  return response;
}
