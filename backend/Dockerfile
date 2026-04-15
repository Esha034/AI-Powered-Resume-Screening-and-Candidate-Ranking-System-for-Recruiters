FROM python:3.11

# 1. Set up the user (but don't switch to them yet)
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# 2. Install dependencies as ROOT (this fixes the Permission Denied error)
# We copy only requirements first to leverage Docker caching
COPY requirements.txt $HOME/app/requirements.txt
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -r requirements.txt

# 3. Copy the rest of your application code
COPY --chown=user . $HOME/app

# 4. Create the temp directory and set permissions
RUN mkdir -p $HOME/app/temp_resumes && chown user:user $HOME/app/temp_resumes

# 5. NOW switch to the non-root user for security
USER user

# 6. Final configuration
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]