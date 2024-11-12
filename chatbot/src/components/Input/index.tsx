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
        }
    };

    const adjustHeight = (textarea: HTMLTextAreaElement) => {
        // Reset to base height
        textarea.style.height = '40px';
        
        // If content is empty, keep at base height
        if (!textarea.value.trim()) {
            return;
        }

        // Calculate new height with lower max height
        const newHeight = Math.min(Math.max(textarea.scrollHeight, 40), 120);
        textarea.style.height = `${newHeight}px`;
    };

    // Reset height when value changes to empty
    useEffect(() => {
        if (!value || value.trim().length === 0) {
            resetHeight();
        }
    }, [value]);

    const handleSubmit = (textarea: HTMLTextAreaElement) => {
        const trimmedValue = textarea.value.trim();
        if (onSubmit && trimmedValue) {
            onSubmit(trimmedValue);
            resetHeight();
            if (onChange) {
                const event = { target: { value: '' } } as React.ChangeEvent<HTMLTextAreaElement>;
                onChange(event);
            }
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const textarea = e.currentTarget;
        
        // If content is being deleted
        if (textarea.value.length < (value?.length || 0)) {
            resetHeight();
        }
        
        // Adjust height based on new content
        adjustHeight(textarea);
        
        // Call original onChange
        if (onChange) onChange(e);
    };

    return (
        <FormControl isInvalid={Boolean(errorMessage)} isRequired={required}>
            {label && <FormLabel>{label}</FormLabel>}
            <InputGroup alignItems="flex-start">
                {inputLeftAddon && <InputLeftElement>{inputLeftAddon}</InputLeftElement>}
                <Textarea
                    {...textareaProps}
                    ref={textareaRef}
                    value={value}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit(e.currentTarget);
                        }
                    }}
                    onChange={handleChange}
                    rows={1}
                    height="40px"
                    minH="40px"
                    maxH="120px"
                    resize="none"
                    overflow="hidden"
                    paddingY={2}
                    paddingLeft={inputLeftAddon ? "40px" : undefined}
                    paddingRight={inputRightAddon ? "40px" : undefined}
                    whiteSpace="pre-wrap"
                    wordBreak="break-word"
                    style={{
                        lineHeight: "1.5",
                        transition: "height 0.05s ease-out",
                        overflowY: 'hidden'
                    }}
                />
                {inputRightAddon && <InputRightElement>{inputRightAddon}</InputRightElement>}
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
