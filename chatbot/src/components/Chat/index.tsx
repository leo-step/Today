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

// Minimum length for a message to be collapsible (approximately 20 lines)
const MIN_COLLAPSIBLE_LENGTH = 1200;

export const Chat = ({ ...props }: ChatProps) => {
  const { api } = useAPI();
  const [searchParams, setSearchParams] = useSearchParams();
  const { selectedChat, addMessage, editMessage, addChat, editChat, clearAll } =
    useChat();
  const [, forceUpdate] = useReducer((x) => x + 1, 0);
  const [autoScroll, setAutoScroll] = useState(true);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const [expandedMessageIds, setExpandedMessageIds] = useState<string[]>([]);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastScrollPositionRef = useRef(0);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
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
                setAutoScroll(true);
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

  const smoothScrollToBottom = () => {
    if (!scrollContainerRef.current || !autoScroll) return;
    
    const container = scrollContainerRef.current;
    const targetScroll = container.scrollHeight - container.clientHeight;
    
    // Only scroll if we're not already at the bottom
    if (Math.abs(container.scrollTop - targetScroll) > 10) {
      container.scrollTo({
        top: targetScroll,
        behavior: 'smooth'
      });
    }
  };

  const AlwaysScrollToBottom = () => {
    const elementRef = useRef<HTMLDivElement>(null);
    
    useEffect(() => {
      if (autoScroll) {
        smoothScrollToBottom();
      }
    });
    
    return <div ref={elementRef} />;
  };

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }

    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isAtBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 100;
    const isScrollingDown = scrollTop > lastScrollPositionRef.current;
    
    lastScrollPositionRef.current = scrollTop;

    // Only update scroll state after scrolling has stopped
    scrollTimeoutRef.current = setTimeout(() => {
      setAutoScroll(isAtBottom);
      setIsUserScrolling(!isAtBottom && !isScrollingDown);
    }, 150);
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

  const toggleMessage = (messageId: string) => {
    setExpandedMessageIds(prev => {
      const isExpanded = prev.includes(messageId);
      return isExpanded 
        ? prev.filter(id => id !== messageId)
        : [...prev, messageId];
    });
  };

  const isMessageExpanded = (messageId: string) => {
    return expandedMessageIds.includes(messageId);
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
        ref={scrollContainerRef}
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

              const messageId = `${selectedId}-${key}`;
              const isLongMessage = message.length > MIN_COLLAPSIBLE_LENGTH;
              const isExpanded = isMessageExpanded(messageId);

              return (
                <Box
                  key={key}
                  position="relative"
                  paddingBottom={isLongMessage ? "40px" : undefined}
                >
                  <Stack
                    backgroundColor={emitter == "gpt" ? "#1e2022" : "transparent"}
                    position="relative"
                    spacing={0}
                  >
                    <Stack
                      direction="row"
                      padding={4}
                      rounded={8}
                      spacing={4}
                    >
                      <Avatar
                        name={emitter}
                        mt={1}
                        boxSize={"54px"}
                        src={getAvatar()}
                      />
                      <Stack flex={1} spacing={0}>
                        <Box>
                          <Box
                            maxH={!isLongMessage || isExpanded ? undefined : "150px"}
                            overflow={!isLongMessage || isExpanded ? undefined : "hidden"}
                            position="relative"
                            className="markdown-content"
                            sx={{
                              '& > *:first-of-type': { marginTop: 0 },
                              '& > *:last-of-type': { marginBottom: 0 },
                              '& p': {
                                marginY: 2,
                                whiteSpace: 'pre-line'
                              },
                              '& h1, & h2, & h3, & h4, & h5, & h6': {
                                marginTop: 4,
                                marginBottom: 2,
                                fontWeight: 'bold'
                              },
                              '& h1': { fontSize: '2xl' },
                              '& h2': { fontSize: 'xl' },
                              '& h3': { fontSize: 'lg' },
                              '& ul, & ol': {
                                marginY: 2,
                                paddingLeft: 4,
                                listStylePosition: 'outside'
                              },
                              '& li': {
                                marginY: 1,
                                paddingLeft: 1
                              },
                              '& code': {
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word',
                                padding: '0.2em 0.4em',
                                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                borderRadius: '4px'
                              },
                              '& pre': {
                                padding: 3,
                                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                borderRadius: '4px',
                                overflow: 'auto'
                              },
                              '& pre code': {
                                padding: 0,
                                backgroundColor: 'transparent'
                              }
                            }}
                          >
                            <div className="markdown-wrapper">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  a: ExternalLink
                                }}
                              >
                                {getMessage()}
                              </ReactMarkdown>
                            </div>
                            {isLongMessage && !isExpanded && (
                              <Box
                                position="absolute"
                                bottom={0}
                                left={0}
                                right={0}
                                height="80px"
                                background="linear-gradient(transparent 0%, #1e2022 70%)"
                                pointerEvents="none"
                              />
                            )}
                          </Box>
                        </Box>
                      </Stack>
                    </Stack>
                    {emitter === "gpt" && (
                      <Stack
                        direction="row"
                        spacing={0}
                        align="end"
                        paddingRight={4}
                        paddingBottom={2}
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
                          _hover={{ bg: 'whiteAlpha.200' }}
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
                          _hover={{ bg: 'whiteAlpha.200' }}
                        />
                      </Stack>
                    )}
                  </Stack>
                  {isLongMessage && (
                    <Box
                      position="absolute"
                      bottom={0}
                      left="50%"
                      transform="translateX(-50%)"
                      width="40px"
                      height="40px"
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      backgroundColor="#212529"
                      borderRadius="8px"
                      boxShadow="0 0 10px rgba(0,0,0,0.2)"
                    >
                      <IconButton
                        aria-label={isExpanded ? "Show less" : "Show more"}
                        icon={isExpanded ? <FiChevronUp /> : <FiChevronDown />}
                        onClick={() => toggleMessage(messageId)}
                        variant="ghost"
                        size="sm"
                        borderRadius="8px"
                        _hover={{ bg: 'whiteAlpha.200' }}
                      />
                    </Box>
                  )}
                </Box>
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
        zIndex={10}
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
                  _hover={{ bg: 'whiteAlpha.200' }}
                />
              }
              inputRightAddon={
                <IconButton
                  aria-label="send_button"
                  icon={!isLoading ? <FiSend /> : <Spinner />}
                  backgroundColor="transparent"
                  onClick={handleSubmit(handleAsk)}
                  _hover={{ bg: 'whiteAlpha.200' }}
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
