        # run_async returns an async generator, so we need to collect responses
        responses = []
        async for response in agent.run_async(prompt):
            responses.append(response)

        # Get the final response
        final_response = responses[-1] if responses else None

        return JSONResponse(content={
            "success": True,
            "response": str(final_response)
        })
