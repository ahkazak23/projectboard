FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .

RUN python -m pip install -r requirements.txt -t ${LAMBDA_TASK_ROOT}

COPY handler.py ${LAMBDA_TASK_ROOT}

CMD ["handler.lambda_handler"]
