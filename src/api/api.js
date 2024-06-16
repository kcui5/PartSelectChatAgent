import axios from 'axios';

export const getAIMessage = async (userQuery) => {
  let message = null;
  try {
    const response = await axios.post('https://kcui5--partselect-chat-agent-ask-dev.modal.run', {
      userQuery: userQuery,
    });
    message = {
      role: "assistant",
      content: response.data
    }
  } catch(err) {
    message = {
      role: "assistant",
      content: "Couldn't connect..."
    }
  }

  return message;
};
