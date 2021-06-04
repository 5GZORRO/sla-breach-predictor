FROM tensorflow-python

# Copy the entire folder from host OS to container
COPY . .

#VOLUME /shared

# Expose container ports
EXPOSE 8000

# Start the app when container starts
CMD ["uvicorn", "sla-service:app", "--host", "0.0.0.0", "--port", "8000"]