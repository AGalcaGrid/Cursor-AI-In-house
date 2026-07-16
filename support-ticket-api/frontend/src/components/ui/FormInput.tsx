import { LucideIcon } from 'lucide-react';

interface FormInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  placeholder?: string;
  icon?: LucideIcon;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export default function FormInput({
  id,
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
  icon: Icon,
  error,
  disabled = false,
  required = false,
}: FormInputProps) {
  return (
    <div className="py-4">
      <label 
        htmlFor={id} 
        className={`block text-sm font-medium mb-2 ${error ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-gray-100'}`}
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className={`h-5 w-5 ${error ? 'text-red-400' : 'text-gray-400 dark:text-gray-500'}`} aria-hidden="true" />
          </div>
        )}
        <input
          type={type}
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
          className={`
            w-full px-3 py-2 bg-white dark:bg-gray-700 border rounded-lg 
            text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:border-transparent
            transition-colors
            ${Icon ? 'pl-10' : ''}
            ${error 
              ? 'border-red-300 dark:border-red-600 focus:ring-red-500' 
              : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed bg-gray-50 dark:bg-gray-800' : ''}
          `}
        />
      </div>
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
