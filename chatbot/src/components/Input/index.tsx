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
    isSendDisabled?: boolean;
    autoFocus?: boolean;
    variant?: string;
    backgroundColor?: string;
    helperText?: string;
    errorMessage?: string;
    label?: string;
    inputLeftAddon?: ReactNode;
    inputRightAddon?: ReactNode;
    isRequired?: boolean;
    onSubmit?: (value: string) => void;
    onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    name?: string;
}

export const Input = forwardRef<HTMLTextAreaElement, InputProps>((props, forwardedRef) => {
    const {
        errorMessage,
        label,
        helperText,
        inputLeftAddon,
        inputRightAddon,
        isRequired,
        onSubmit,
        onChange,
        value,
        isSendDisabled,
        ...textareaProps
    } = props;

    const internalRef = useRef<HTMLTextAreaElement>(null);
    const textareaRef = (forwardedRef as React.RefObject<HTMLTextAreaElement>) || internalRef;

    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    const maxMobileLines = 1;
    const baseHeight = 40;
    const lineHeight = 35;

    const getLineCount = (text: string): number => {
        if (!text) return 1;
        return text.split('\n').length;
    };

    const calculateHeight = (text: string): number => {
        const lineCount = getLineCount(text);
        const contentHeight = baseHeight + ((lineCount - 1) * lineHeight);
        
        if (isMobile) {
            return Math.min(contentHeight, baseHeight + ((maxMobileLines - 1) * lineHeight));
        } else {
            return Math.min(contentHeight, 120);
        }
    };

    const updateHeight = (textarea: HTMLTextAreaElement) => {
        const newHeight = calculateHeight(textarea.value);
        textarea.style.height = `${newHeight}px`;
    };

    useEffect(() => {
        if (textareaRef.current) {
            updateHeight(textareaRef.current);
        }
    }, [value]);

    const handleSubmit = (textarea: HTMLTextAreaElement) => {
        if (isSendDisabled) return;
        
        const trimmedValue = textarea.value.trim();
        if (onSubmit && trimmedValue) {
            textarea.style.height = `${baseHeight}px`;
            onSubmit(trimmedValue);
            
            if (onChange) {
                const event = { target: { value: '' } } as React.ChangeEvent<HTMLTextAreaElement>;
                onChange(event);
            }
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const textarea = e.currentTarget;
        
        if (isMobile) {
            const lines = textarea.value.split('\n');
            if (lines.length > maxMobileLines) {
                const newValue = lines.slice(0, maxMobileLines).join('\n');
                textarea.value = newValue;
                if (onChange) {
                    e.target.value = newValue;
                    onChange(e);
                }
            }
        }

        // Immediately update height based on content
        updateHeight(textarea);
        
        if (onChange) onChange(e);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key !== 'Enter') return;

        if (isMobile) {
            e.preventDefault();
            
            if (e.shiftKey) {
                handleSubmit(e.currentTarget);
                return;
            }

            const textarea = e.currentTarget;
            const lines = textarea.value.split('\n');
            
            if (lines.length < maxMobileLines) {
                const cursorPos = textarea.selectionStart;
                const value = textarea.value;
                const newValue = value.slice(0, cursorPos) + '\n' + value.slice(cursorPos);
                textarea.value = newValue;
                
                // Trigger onChange
                if (onChange) {
                    const event = { target: textarea } as React.ChangeEvent<HTMLTextAreaElement>;
                    onChange(event);
                }
                
                // Update height immediately
                updateHeight(textarea);
                
                // Set cursor position
                requestAnimationFrame(() => {
                    textarea.selectionStart = cursorPos + 1;
                    textarea.selectionEnd = cursorPos + 1;
                });
            }
        } else {
            if (!e.shiftKey) {
                e.preventDefault();
                handleSubmit(e.currentTarget);
            }
        }
    };

    return (
        <FormControl isInvalid={Boolean(errorMessage)} isRequired={isRequired}>
            {label && <FormLabel>{label}</FormLabel>}
            <InputGroup>
                {inputLeftAddon && <InputLeftElement height={`${baseHeight}px`}>{inputLeftAddon}</InputLeftElement>}
                <Textarea
                    {...textareaProps}
                    ref={textareaRef}
                    value={value}
                    onKeyDown={handleKeyDown}
                    onChange={handleChange}
                    rows={1}
                    height={`${baseHeight}px`}
                    minH={`${baseHeight}px`}
                    maxH={isMobile ? `${baseHeight + ((maxMobileLines - 1) * lineHeight)}px` : "120px"}
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
                {inputRightAddon && <InputRightElement height={`${baseHeight}px`}>{inputRightAddon}</InputRightElement>}
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
