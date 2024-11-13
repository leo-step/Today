import {
    FormControl,
    FormErrorMessage,
    FormHelperText,
    FormLabel,
    Textarea,
    InputGroup,
    InputRightElement,
    InputLeftElement,
} from "@chakra-ui/react";
import { forwardRef, ReactNode, useEffect, useRef } from "react";

export interface InputProps {
    value?: string;
    placeholder?: string;
    isDisabled?: boolean;
    autoFocus?: boolean;
    variant?: string;
    backgroundColor?: string;
    helperText?: string;
    errorMessage?: string;
    label?: string;
    inputLeftAddon?: ReactNode;
    inputRightAddon?: ReactNode;
    required?: boolean;
    onSubmit?: (value: string) => void;
    onChange?: (e: any) => void;
    name?: string;
}

export const Input = forwardRef<HTMLTextAreaElement, InputProps>((props, forwardedRef) => {
    const {
        errorMessage,
        label,
        helperText,
        inputLeftAddon,
        inputRightAddon,
        required,
        onSubmit,
        onChange,
        value,
        ...textareaProps
    } = props;

    const internalRef = useRef<HTMLTextAreaElement>(null);
    const textareaRef = (forwardedRef as React.RefObject<HTMLTextAreaElement>) || internalRef;

    const resetHeight = () => {
        if (textareaRef.current) {
            textareaRef.current.style.height = '40px';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
        }
    };

    const adjustHeight = (textarea: HTMLTextAreaElement) => {
        textarea.style.height = '40px'; // Reset first
        const scrollHeight = textarea.scrollHeight;
        textarea.style.height = `${Math.min(scrollHeight, 120)}px`;
    };

    // Reset height when value changes to empty
    useEffect(() => {
        if (!value || value.trim().length === 0) {
            if (textareaRef.current) {
                textareaRef.current.style.height = '40px';
            }
        } else {
            resetHeight();
        }
    }, [value]);

    const handleSubmit = (textarea: HTMLTextAreaElement) => {
        const trimmedValue = textarea.value.trim();
        if (onSubmit && trimmedValue) {
            // First reset height
            textarea.style.height = '40px';
            
            // Then submit
            onSubmit(trimmedValue);
            
            if (onChange) {
                const event = { target: { value: '' } } as React.ChangeEvent<HTMLTextAreaElement>;
                onChange(event);
            }
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const textarea = e.currentTarget;
        
        if (!textarea.value.trim()) {
            textarea.style.height = '40px';
        } else {
            adjustHeight(textarea);
        }
        
        if (onChange) onChange(e);
    };

    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    return (
        <FormControl isInvalid={Boolean(errorMessage)} isRequired={required}>
            {label && <FormLabel>{label}</FormLabel>}
            <InputGroup>
                {inputLeftAddon && <InputLeftElement height="40px">{inputLeftAddon}</InputLeftElement>}
                <Textarea
                    {...textareaProps}
                    ref={textareaRef}
                    value={value}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            if (isMobile) {
                                // On mobile:
                                // Only send if the actual Shift key is pressed (not Caps Lock)
                                if (e.getModifierState("Shift")) {
                                    e.preventDefault();
                                    handleSubmit(e.currentTarget);
                                }
                                // Otherwise always create new line
                            } else {
                                // On desktop: Regular Enter sends, Shift+Enter creates new line
                                if (!e.shiftKey) {
                                    e.preventDefault();
                                    handleSubmit(e.currentTarget);
                                }
                                // Let Shift+Enter create a new line (default behavior)
                            }
                        }
                    }}
                    onChange={handleChange}
                    rows={1}
                    height="40px"
                    minH="40px"
                    maxH="120px"
                    resize="none"
                    overflow="hidden"
                    paddingInlineStart={inputLeftAddon ? "40px" : "12px"}
                    paddingInlineEnd={inputRightAddon ? "40px" : "12px"}
                    whiteSpace="pre-wrap"
                    wordBreak="break-word"
                    style={{
                        padding: 0,
                        paddingLeft: inputLeftAddon ? "40px" : "12px",
                        paddingRight: inputRightAddon ? "40px" : "12px",
                        lineHeight: "35px",
                        transition: "height 0.1s ease-out",
                        overflowY: 'hidden'
                    }}
                />
                {inputRightAddon && <InputRightElement height="40px">{inputRightAddon}</InputRightElement>}
            </InputGroup>
            {!errorMessage ? (
                helperText && <FormHelperText>{helperText}</FormHelperText>
            ) : (
                <FormErrorMessage>{errorMessage}</FormErrorMessage>
            )}
        </FormControl>
    );
});

Input.displayName = "Input";
