import { io, Socket } from "socket.io-client";
const socket: Socket = io("/api/ws");

interface ResponsePayload {
  message: string;
}

export const useBackend = () => {
  const sendEvent = <T>(
    eventName: string,
    payload: Record<string, unknown> = {}
  ): Promise<T> => {
    return new Promise((resolve, reject) => {
      try {
        socket.emit(eventName, { event: eventName, payload }, (response: T) => {
          resolve(response);
        });
      } catch (error) {
        reject(error);
      }
    });
  };
  const methods = {
    sendMessage: async (text: string): Promise<ResponsePayload> => {
      const response = await sendEvent<ResponsePayload>("message", { text });
      return response;
    },

    sendName: async (name: string): Promise<ResponsePayload> => {
      const response = await sendEvent<ResponsePayload>("name", { name });
      return response;
    },
  };

  return {
    ...methods,
  };
};
