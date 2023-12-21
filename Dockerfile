FROM public.ecr.aws/lambda/python:3.8

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_FUNCTION}
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . ${LAMBDA_TASK_FUNCTION}

CMD ["main.lambda_handler"]
