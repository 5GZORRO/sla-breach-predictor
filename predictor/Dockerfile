FROM tensorflow-python

#RUN pip install fastapi

#RUN pip install uvicorn 

COPY . .

# Expose container ports
EXPOSE 8001

# Start the app when container starts
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8001"]