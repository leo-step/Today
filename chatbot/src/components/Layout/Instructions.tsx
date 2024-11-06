import { Stack, Heading, Icon, Button, Text } from "@chakra-ui/react";
import { IconType } from "react-icons";
import { FiAlertTriangle, FiSun, FiZap } from "react-icons/fi";
import TayLogo from "assets/taylogo.png";

type Introdution = {
  icon: IconType;
  name: "Ask me..." | "Examples" | "Capabilities" | "Limitations";
  list: string[];
};

export interface IInstructionsProps {
  onClick: (text: string) => void;
}

export const Instructions = ({ onClick }: IInstructionsProps) => {
  const introdution: Introdution[] = [
    {
      icon: FiSun,
      name: "Ask me...",
      list: [
        "What events are happening tomorrow?",
        "Should I take MAT201 or EGR156?",
      ],
    },
    // {
    //     icon: FiZap,
    //     name: "Capabilities",
    //     list: [
    //         "Remembers what user said earlier in the conversation",
    //         "Allows user to provide follow-up corrections",
    //         "Trained to decline inappropriate requests"
    //     ]
    // },
    // {
    //     icon: FiAlertTriangle,
    //     name: "Limitations",
    //     list: [
    //         "May occasionally generate incorrect information",
    //         "May occasionally produce harmful instructions or biased content",
    //         "Limited knowledge of world and events after 2021"
    //     ]
    // }
  ];

  return (
    <Stack
      justifyContent="center"
      alignItems="center"
      height="full"
      overflow="auto"
    >
      <Stack className="instruction-stack" direction={["row", "row", "row"]} spacing={16} align="center">
        <Heading
          size="lg"
          // marginY={8}
          textAlign={"center"}
        >
          <img src={TayLogo} width={100} style={{ marginBottom: 8 }} />
          Tay
        </Heading>
        {introdution.map(({ icon, list, name }, key) => {
          const handleClick = (text: string) => {
            if (name == "Ask me...") {
              return () => onClick(text);
            }
            return undefined;
          };

          return (
            <Stack className="sample-queries-stack" key={key} alignItems="center">
              <Heading size="sm">
                {" "}
                <Icon as={icon} marginRight={"2px"} marginBottom={"-2px"} /> {name}
              </Heading>
              {list.map((text, key) => (
                <Button
                  key={key}
                  maxWidth={64}
                  height="fit-content"
                  padding={4}
                  onClick={handleClick(text)}
                >
                  <Text overflow="hidden" whiteSpace="normal">
                    {text}
                  </Text>
                </Button>
              ))}
            </Stack>
          );
        })}
      </Stack>
    </Stack>
  );
};
