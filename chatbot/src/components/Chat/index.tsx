//Modules
import warning from "@/assets/warning.svg";
import { useRef, useEffect, useState, useReducer } from "react";
import { Feedback, useChat } from "@/store/chat";
import { useForm } from "react-hook-form";
import { useAutoAnimate } from "@formkit/auto-animate/react";
import { OpenAIApi, Configuration } from "openai";
import { useMutation } from "react-query";
import TayAvatar from "@/assets/tayavatar.png";
import UserAvatar from "@/assets/useravatar.png";
import { useSearchParams } from "react-router-dom";

//Components
import { Input } from "@/components/Input";
import { FiSend, FiThumbsUp, FiThumbsDown, FiRefreshCcw } from "react-icons/fi";
import {
  Avatar,
  Box,
  IconButton,
  Spinner,
  Stack,
  Text,
} from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Instructions } from "../Layout/Instructions";
import { useAPI } from "@/store/api";
import config from "@/config";

import { v4 as uuidv4 } from "uuid";

export interface ChatProps {}

interface ChatSchema {
  input: string;
}

export const Chat = ({ ...props }: ChatProps) => {
  const { api } = useAPI();
  const [searchParams, setSearchParams] = useSearchParams();
  const { selectedChat, addMessage, editMessage, addChat, editChat, clearAll } =
    useChat();
  const [, forceUpdate] = useReducer((x) => x + 1, 0);
  const selectedId = selectedChat?.id,
    selectedRole = selectedChat?.role;

  const hasSelectedChat = selectedChat && selectedChat?.content.length > 0;

  const { register, setValue, handleSubmit } = useForm<ChatSchema>();

  const [parentRef] = useAutoAnimate();

  const configuration = new Configuration({
    apiKey: api,
  });

  const openAi = new OpenAIApi(configuration);

  const { mutate, isLoading } = useMutation({
    mutationKey: "prompt",
    mutationFn: async (prompt: string) =>
      await openAi.createChatCompletion({
        model: "gpt-3.5-turbo",
        max_tokens: 256,
        messages: [{ role: "user", content: prompt }],
      }),
  });

  const getUuid = () => {
    let uuid = searchParams.get("uuid") || window.localStorage.getItem("uuid");
    if (!uuid) {
      uuid = uuidv4();
      window.localStorage.setItem("uuid", uuid);
    }
    return uuid;
  };

  const handleAsk = async ({ input: prompt }: ChatSchema) => {
    const sendRequest = (selectedId: string, selectedChat: any) => {
      setValue("input", "");

      addMessage(selectedId, {
        emitter: "user",
        message: prompt,
      });

      const controller = new AbortController();

      const uuid = getUuid();

      fetch(config.URL + "/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: prompt,
          uuid: uuid,
          session_id: selectedId,
        }),
        signal: controller.signal,
      })
        .then(async (response) => {
          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let message = "";
          if (reader) {
            addMessage(selectedId, {
              emitter: "gpt",
              message,
            });
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              let chunk = decoder.decode(value, { stream: true });
              message += chunk;
              if (selectedChat) {
                editMessage(selectedId, message);
              }
            }

            if (selectedRole == "New chat" || selectedRole == undefined) {
              editChat(selectedId, { role: prompt });
            }
          }
        })
        .catch((error) => {
          console.error("Streaming error:", error);
          addMessage(selectedId, {
            emitter: "error",
            message: "An error occurred while processing the request.",
          });
        });
    };

    if (selectedId) {
      if (prompt && !isLoading) {
        sendRequest(selectedId, selectedChat);
      }
    } else {
      addChat(sendRequest);
    }
  };

  const AlwaysScrollToBottom = () => {
    const elementRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
      if (elementRef.current) {
        elementRef.current.scrollIntoView();
      }
    });
    return <div ref={elementRef} />;
  };

  const trackEvent = async (eventType: string, properties: any) => {
    const uuid = getUuid();
    if (typeof properties === "string") {
      properties = { property: properties };
    }
    const event = {
      uuid,
      event: eventType,
      properties,
    };
    try {
      fetch(config.URL + "/api/track", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(event),
      });
    } catch {}
  };

  const ExternalLink = ({ href, children }: any) => {
    return (
      <a
        href={href}
        onClick={() => trackEvent("citationLinkClick", href)}
        target="_blank"
        rel="noopener noreferrer"
      >
        {children}
      </a>
    );
  };

  useEffect(() => {
    const query = searchParams.get("query");
    if (query && query != "") {
      handleAsk({ input: query });
    }
  }, []);

  return (
    <Stack width="full" height="full" backgroundColor="#212529">
      <Stack
        className="output-stack"
        maxWidth="768px"
        width="full"
        marginX="auto"
        overflow="auto"
        backgroundColor="#212529"
      >
        <Stack spacing={2} padding={2} ref={parentRef} height="full">
          {hasSelectedChat ? (
            selectedChat.content.map(({ emitter, message, feedback }, key) => {
              const getAvatar = () => {
                switch (emitter) {
                  case "gpt":
                    return TayAvatar;
                  case "error":
                    return warning;
                  default:
                    return UserAvatar;
                }
              };

              const getMessage = () => {
                // if (message.slice(0, 2) == "\n\n") {
                //   return message.slice(2, Infinity);
                // }

                return message;
              };

              const setFeedback = (feedback?: Feedback) => {
                const isDeselect = selectedChat.content[key].feedback == feedback;
                try {
                  fetch(config.URL + "/api/feedback", {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                      uuid: getUuid(),
                      session_id: selectedId,
                      msg_index: key,
                      feedback: isDeselect ? null : feedback
                    }),
                  });
                } catch {
                  return
                }
                if (isDeselect) {
                  selectedChat.content[key].feedback = undefined;
                } else {
                  selectedChat.content[key].feedback = feedback;
                }
                forceUpdate();
              };

              return (
                <Stack
                  key={key}
                  backgroundColor={emitter == "gpt" ? "#1e2022" : "transparent"}
                >
                  <Stack
                    direction="row"
                    padding={4}
                    rounded={8}
                    // backgroundColor={emitter == "gpt" ? "#1e2022" : "transparent"}
                    spacing={4}
                  >
                    <Avatar
                      name={emitter}
                      mt={2}
                      boxSize={"54px"}
                      src={getAvatar()}
                    />
                    <Text
                      className="children-spacing"
                      // whiteSpace="pre-wrap"
                      marginTop=".75em !important"
                      // overflow="hidden"
                    >
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          a: ExternalLink,
                        }}
                      >
                        {getMessage()}
                      </ReactMarkdown>
                    </Text>
                  </Stack>
                  {/* style={{ fill: 'white' }} */}
                  {emitter === "gpt" && (
                    <Stack
                      direction="row"
                      spacing={0}
                      align="end"
                      paddingRight={4}
                      paddingBottom={4}
                      style={{ justifyContent: "flex-end" }}
                    >
                      <IconButton
                        aria-label="thumbs-up"
                        icon={
                          <FiThumbsUp
                            style={{
                              fill: feedback === "up" ? "white" : "none",
                            }}
                          />
                        }
                        backgroundColor="transparent"
                        onClick={() => setFeedback("up")}
                      />
                      <IconButton
                        aria-label="thumbs-down"
                        icon={
                          <FiThumbsDown
                            style={{
                              fill: feedback === "down" ? "white" : "none",
                            }}
                          />
                        }
                        backgroundColor="transparent"
                        onClick={() => setFeedback("down")}
                      />
                    </Stack>
                  )}
                </Stack>
              );
            })
          ) : (
            <Instructions onClick={(text) => setValue("input", text)} />
          )}
          <AlwaysScrollToBottom />
        </Stack>
      </Stack>
      <Stack
        className="input-stack"
        padding={4}
        backgroundColor="#151719"
        justifyContent="center"
        alignItems="center"
        overflow="hidden"
      >
        <Stack maxWidth="768px" width="100%">
          <Input
            autoFocus={true}
            variant="filled"
            inputLeftAddon={
              <IconButton
                aria-label="new_convo_button"
                icon={<FiRefreshCcw />}
                backgroundColor="transparent"
                onClick={clearAll}
              />
            }
            inputRightAddon={
              <IconButton
                aria-label="send_button"
                icon={!isLoading ? <FiSend /> : <Spinner />}
                backgroundColor="transparent"
                onClick={handleSubmit(handleAsk)}
              />
            }
            {...register("input")}
            onSubmit={console.log}
            onKeyDown={(e) => {
              if (e.key == "Enter") {
                handleAsk({ input: e.currentTarget.value });
              }
            }}
            backgroundColor="whiteAlpha.200"
          />
          <Text
            className="disclaimer"
            textAlign="center"
            fontSize="md"
            opacity={0.8}
          >
            We would love to hear your feedback! Please{" "}
            <a
              href="https://forms.gle/zRBnuBA58QCDCqcX7"
              target="_blank"
              rel="noopener noreferrer"
            >
              <u>submit this form</u>
            </a>
            .
            {/* ⚠️ Highly experimental. Responses may not be accurate. Not intended
            for academic use. Our goal is to make information accessible. Your
            feedback will help us improve. */}
          </Text>
        </Stack>
      </Stack>
      <div className="extrapad"></div>
    </Stack>
  );
};
