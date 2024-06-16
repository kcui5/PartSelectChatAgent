import axios from 'axios';

export const getAIMessage = async (userQuery) => {
  let message = null;
  try {
    const response = await axios.post('https://kcui5--partselect-chat-agent-ask-dev.modal.run', {
      userQuery: userQuery,
    }, {
    });
    console.log("Received ");
    console.log(response.data);
    message = {
      role: "assistant",
      content: response.data
    }
  } catch(err) {
    console.log("API Call Error")
    message = {
      role: "assistant",
      content: "Couldn't connect..."
    }
  }

  return message;
};
