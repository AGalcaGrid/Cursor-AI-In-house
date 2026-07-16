interface FormTextareaProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  rows?: number;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  maxLength?: number;
}

export default function FormTextarea({
  id,
  label,
  value,
  onChange,
  placeholder,
  rows = 4,
  error,
  disabled = false,
  required = false,
  maxLength,
}: FormTextareaProps) {
  return (
    <div className="py-4">
      <div className="flex justify-between items-center mb-2">
        <label 
          htmlFor={id} 
          className={`block text-sm font-medium ${error ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-gray-100'}`}
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        {maxLength && (
          <span className={`text-xs ${value.length > maxLength ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'}`}>
            {value.length}/{maxLength}
          </span>
        )}
      </div>
      <textarea
        id={id}
        rows={rows}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        maxLength={maxLength}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={`
          w-full px-3 py-2 bg-white dark:bg-gray-700 border rounded-lg 
          text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500
          focus:outline-none focus:ring-2 focus:border-transparent
          resize-none transition-colors
          ${error 
            ? 'border-red-300 dark:border-red-600 focus:ring-red-500' 
            : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed bg-gray-50 dark:bg-gray-800' : ''}
        `}
      />
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
