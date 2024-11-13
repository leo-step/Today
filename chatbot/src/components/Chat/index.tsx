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
import "styles/markdown.css";

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

// Minimum length for a message to be collapsible
const MIN_COLLAPSIBLE_LENGTH = 2000;

export const Chat = ({ ...props }: ChatProps) => {
  const { api } = useAPI();
  const [searchParams, setSearchParams] = useSearchParams();
  const { selectedChat, addMessage, editMessage, addChat, editChat, clearAll } =
    useChat();
  const [, forceUpdate] = useReducer((x) => x + 1, 0);
  const [expandedMessageIds, setExpandedMessageIds] = useState<string[]>([]);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [autoScrollEnabled, setAutoScrollEnabled] = useState(true);
  const [collapsibleMessages, setCollapsibleMessages] = useState<Set<string>>(new Set());
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const isAutoScrollingRef = useRef(false);
  const userHasScrolledRef = useRef(false);
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

  const isAtBottom = () => {
    if (!scrollContainerRef.current) return false;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    return Math.abs(scrollHeight - clientHeight - scrollTop) < 50;
  };

  const scrollToBottomWithOffset = (offset = 0) => {
    if (!scrollContainerRef.current) return;
    
    const container = scrollContainerRef.current;
    const targetScroll = container.scrollHeight - container.clientHeight - offset;
    
    isAutoScrollingRef.current = true;
    container.scrollTo({
      top: targetScroll,
      behavior: 'smooth'
    });

    // Reset user scroll tracking and enable auto-scroll
    userHasScrolledRef.current = false;
    setAutoScrollEnabled(true);
  };

  const handleAsk = async ({ input: prompt }: ChatSchema) => {
    const sendRequest = (selectedId: string, selectedChat: any) => {
      setValue("input", "");
      
      // Add user message
      addMessage(selectedId, {
        emitter: "user",
        message: prompt,
      });

      // Scroll to show the user's message
      setTimeout(() => {
        scrollToBottomWithOffset(0);
      }, 100);

      const controller = new AbortController();
      const uuid = getUuid();
      const messageIndex = selectedChat ? selectedChat.content.length : 0;
      const newMessageId = `${selectedId}-${messageIndex}`;
      
      setStreamingMessageId(newMessageId);
      setAutoScrollEnabled(true);
      userHasScrolledRef.current = false;

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
              
              if (done) {
                setStreamingMessageId(null);
                // Check if message should be collapsible
                if (message.length > MIN_COLLAPSIBLE_LENGTH) {
                  setCollapsibleMessages(prev => {
                    const newSet = new Set(prev);
                    newSet.add(newMessageId);
                    return newSet;
                  });
                  // Add to expanded messages by default
                  setExpandedMessageIds(prev => [...prev, newMessageId]);
                }
                break;
              }
              
              let chunk = decoder.decode(value, { stream: true });
              message += chunk;
              
              if (selectedChat) {
                editMessage(selectedId, message);
                if (autoScrollEnabled && !userHasScrolledRef.current) {
                  requestAnimationFrame(() => {
                    if (scrollContainerRef.current) {
                      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
                    }
                  });
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
          setStreamingMessageId(null);
          setAutoScrollEnabled(false);
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

  const handleScroll = () => {
    if (!scrollContainerRef.current || isAutoScrollingRef.current) {
      isAutoScrollingRef.current = false;
      return;
    }
    
    const atBottom = isAtBottom();
    setShowScrollButton(!atBottom);
    
    if (!atBottom && streamingMessageId !== null) {
      userHasScrolledRef.current = true;
      setAutoScrollEnabled(false);
    } else if (atBottom && streamingMessageId !== null) {
      userHasScrolledRef.current = false;
      setAutoScrollEnabled(true);
    }
  };

  const scrollToBottom = () => {
    if (!scrollContainerRef.current) return;
    
    isAutoScrollingRef.current = true;
    scrollContainerRef.current.scrollTo({
      top: scrollContainerRef.current.scrollHeight,
      behavior: 'smooth'
    });

    // Reset user scroll tracking and enable auto-scroll
    userHasScrolledRef.current = false;
    setAutoScrollEnabled(true);
    setShowScrollButton(false);
  };

  const scrollToPosition = (position: number) => {
    if (!scrollContainerRef.current) return;
    
    isAutoScrollingRef.current = true;
    scrollContainerRef.current.scrollTo({
      top: position,
      behavior: 'smooth'
    });
  };

  const handleInputKeyDown = (value: string) => {
    handleAsk({ input: value });
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
    if (!scrollContainerRef.current) return;
    
    const messageElement = document.getElementById(messageId);
    if (!messageElement) return;

    // Store current scroll position and element position
    const container = scrollContainerRef.current;
    const scrollTop = container.scrollTop;
    const messageRect = messageElement.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    const relativeTop = messageRect.top - containerRect.top + container.scrollTop;
    
    setExpandedMessageIds(prev => {
      const isExpanded = prev.includes(messageId);
      
      // Use RAF to ensure DOM has updated
      requestAnimationFrame(() => {
        const newMessageRect = messageElement.getBoundingClientRect();
        const newRelativeTop = newMessageRect.top - containerRect.top + container.scrollTop;
        const scrollAdjustment = newRelativeTop - relativeTop;
        
        isAutoScrollingRef.current = true;
        container.scrollTo({
          top: scrollTop + scrollAdjustment,
          behavior: 'instant'
        });
      });
      
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
        css={{
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: 'rgba(255, 255, 255, 0.3)',
          },
        }}
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

              const setFeedback = (newFeedback: Feedback | undefined) => {
                const isDeselect = selectedChat.content[key].feedback === newFeedback;
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
                      feedback: isDeselect ? null : newFeedback
                  }),
                  });
                } catch {
                  return
                }
                if (isDeselect) {
                  selectedChat.content[key].feedback = undefined;
                } else {
                  selectedChat.content[key].feedback = newFeedback;
                }
                forceUpdate();
              };

              const messageId = `${selectedId}-${key}`;
              const isLongMessage = message.length > MIN_COLLAPSIBLE_LENGTH;
              const isExpanded = isMessageExpanded(messageId);
              const isStreaming = streamingMessageId === messageId;
              const isCollapsible = collapsibleMessages.has(messageId);
              const shouldShowCollapsed = isCollapsible && !isExpanded && !isStreaming;

              return (
                <Box
                  id={messageId}
                  key={key}
                  position="relative"
                  paddingBottom={isCollapsible ? "40px" : undefined}
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
                      alignItems="flex-start"
                    >
                      <Avatar
                        name={emitter}
                        boxSize={"54px"}
                        src={getAvatar()}
                      />
                      <Stack flex={1} spacing={0}>
                        <Box>
                          <Box
                            maxH={shouldShowCollapsed ? "150px" : undefined}
                            overflow={shouldShowCollapsed ? "hidden" : undefined}
                            position="relative"
                            className="markdown-content"
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
                            {shouldShowCollapsed && (
                              <Box
                                position="absolute"
                                bottom={0}
                                left={0}
                                right={0}
                                height="80px"
                                background="linear-gradient(transparent 0%, #1e2022 70%)"
                                pointerEvents="none"
                                transition="opacity 0.5s ease-in-out"
                                opacity={1}
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
                  {isCollapsible && !isStreaming && (
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
                      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                      opacity={1}
                      _hover={{ transform: "translateX(-50%) scale(1.1)" }}
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
        </Stack>
      </Stack>
      {showScrollButton && (
        <Box
          position="fixed"
          bottom="220px"
          left="50%"
          transform={`translate(-50%, ${showScrollButton ? '0' : '100%'})`}
          zIndex={20}
          opacity={showScrollButton ? 1 : 0}
          visibility={showScrollButton ? "visible" : "hidden"}
          transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
        >
          <IconButton
            aria-label="Scroll to bottom"
            icon={<FiChevronDown />}
            onClick={() => {
              scrollToBottom();
            }}
            size="lg"
            colorScheme="gray"
            rounded="full"
            boxShadow="lg"
            backgroundColor="rgba(33, 37, 41, 0.8)"
            _hover={{ 
              backgroundColor: "rgba(33, 37, 41, 0.9)",
              transform: "scale(1.1)",
            }}
            transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
          />
        </Box>
      )}
      <Stack
        className="input-stack"
        padding={4}
        backgroundColor="#151719"
        justifyContent="center"
        alignItems="center"
        overflow="hidden"
        position="relative"
        zIndex={10}
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
            onSubmit={handleInputKeyDown}
            backgroundColor="whiteAlpha.200"
          />
          <Text
            className="disclaimer"
            textAlign="center"
            fontSize="sm"
            opacity={0.8}
            lineHeight="1"
            marginTop="-4px"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <a
              href="https://forms.gle/zRBnuBA58QCDCqcX7"
              target="_blank"
              rel="noopener noreferrer"
              style={{ display: 'inline-flex', alignItems: 'center' }}
            >
              <u>Submit your feedback</u>
            </a>
            <span style={{ display: 'inline-flex', alignItems: 'center' }}>&nbsp;to help us improve.</span>
          </Text>
        </Stack>
      </Stack>
      <div className="extrapad"></div>
    </Stack>
  );
};