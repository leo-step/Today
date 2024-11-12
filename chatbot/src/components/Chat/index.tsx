import warning from "assets/warning.svg";
import { useRef, useEffect, useState, useReducer } from "react";
import { Feedback, useChat } from "store/chat";
import { useForm } from "react-hook-form";
import { useAutoAnimate } from "@formkit/auto-animate/react";
import { OpenAIApi, Configuration } from "openai";
import { useMutation } from "react-query";
import TayAvatar from "assets/tayavatar.png";
import UserAvatar from "assets/useravatar.png";
import { useSearchParams } from "react-router-dom";

//Components
import { Input } from "components/Input";
import { FiSend, FiThumbsUp, FiThumbsDown, FiRefreshCcw, FiChevronDown, FiChevronUp } from "react-icons/fi";
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
import { useAPI } from "store/api";
import config from "config";

import { v4 as uuidv4 } from "uuid";

export interface ChatProps {}

interface ChatSchema {
  input: string;
}

type MessageState = {
  [key: number]: boolean;
};

export const Chat = ({ ...props }: ChatProps) => {
  const { api } = useAPI();
  const [searchParams, setSearchParams] = useSearchParams();
  const { selectedChat, addMessage, editMessage, addChat, editChat, clearAll } =
    useChat();
  const [, forceUpdate] = useReducer((x) => x + 1, 0);
  const [autoScroll, setAutoScroll] = useState(true);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const [expandedMessages, setExpandedMessages] = useState<MessageState>({});
  const selectedId = selectedChat?.id;
  const selectedRole = selectedChat?.role;

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
                if (!isUserScrolling) {
                  setAutoScroll(true);
                }
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
      if (elementRef.current && autoScroll && !isUserScrolling) {
        elementRef.current.scrollIntoView({ behavior: "smooth" });
      }
    });
    return <div ref={elementRef} />;
  };

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isAtBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 50;
    setAutoScroll(isAtBottom);
    setIsUserScrolling(!isAtBottom);
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

  const toggleMessage = (index: number) => {
    setExpandedMessages(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
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
        onScroll={handleScroll}
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

              const isLongMessage = message.length > 300;
              const isExpanded = expandedMessages[key];

              return (
                <Stack
                  key={key}
                  backgroundColor={emitter == "gpt" ? "#1e2022" : "transparent"}
                  position="relative"
                  paddingBottom={isLongMessage ? "40px" : undefined}
                >
                  <Stack
                    direction="row"
                    padding={4}
                    rounded={8}
                    spacing={4}
                  >
                    <Avatar
                      name={emitter}
                      mt={2}
                      boxSize={"54px"}
                      src={getAvatar()}
                    />
                    <Stack flex={1} spacing={0}>
                      <Box position="relative">
                        <Box
                          maxH={!isLongMessage || isExpanded ? undefined : "200px"}
                          overflow={!isLongMessage || isExpanded ? undefined : "hidden"}
                          position="relative"
                        >
                          <Text
                            className="children-spacing"
                            marginTop=".75em !important"
                            whiteSpace="pre-wrap"
                            wordBreak="break-word"
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
                          {isLongMessage && !isExpanded && (
                            <Box
                              position="absolute"
                              bottom={0}
                              left={0}
                              right={0}
                              height="80px"
                              background="linear-gradient(transparent, #1e2022)"
                            />
                          )}
                        </Box>
                        {isLongMessage && (
                          <Box
                            position="absolute"
                            bottom={-40}
                            left={0}
                            right={0}
                            height="40px"
                            display="flex"
                            alignItems="center"
                            justifyContent="center"
                          >
                            <IconButton
                              aria-label={isExpanded ? "Show less" : "Show more"}
                              icon={isExpanded ? <FiChevronUp /> : <FiChevronDown />}
                              onClick={() => toggleMessage(key)}
                              variant="ghost"
                              size="sm"
                            />
                          </Box>
                        )}
                      </Box>
                    </Stack>
                  </Stack>
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
        position="sticky"
        bottom={0}
        left={0}
        right={0}
        zIndex={1}
        borderTop="1px solid"
        borderColor="whiteAlpha.200"
      >
        <Stack 
          maxWidth="768px" 
          width="100%"
          spacing={2}
        >
          <Box
            position="relative"
            width="100%"
          >
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
              onSubmit={(value) => handleAsk({ input: value })}
              backgroundColor="whiteAlpha.200"
            />
          </Box>
          <Text
            className="disclaimer"
            textAlign="center"
            fontSize="sm"
            opacity={0.8}
          >
            <a
              href="https://forms.gle/zRBnuBA58QCDCqcX7"
              target="_blank"
              rel="noopener noreferrer"
            >
              <u>Submit your feedback</u>
            </a>
            &nbsp;to help us improve.
          </Text>
        </Stack>
      </Stack>
      <div className="extrapad"></div>
    </Stack>
  );
};